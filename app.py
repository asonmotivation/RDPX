import os
import json
import requests
import datetime
from dateutil import parser
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from dotenv import load_dotenv
from github import Github
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")
app.config['SESSION_TYPE'] = 'filesystem'

# Default admin credentials (should be changed in production)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD_HASH", generate_password_hash("admin"))

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

def get_github_api():
    """Initialize GitHub API client with token"""
    if not GITHUB_TOKEN:
        return None
    return Github(GITHUB_TOKEN)

def get_workflow_runs(limit=10):
    """Get recent workflow runs from the GitHub repository"""
    g = get_github_api()
    if not g:
        return []
    
    try:
        repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
        workflow_runs = list(repo.get_workflow_runs()[:limit])
        
        runs_data = []
        for run in workflow_runs:
            # Calculate uptime and remaining time
            created_at = run.created_at
            now = datetime.datetime.now(created_at.tzinfo)
            uptime = now - created_at
            
            # GitHub Actions workflows typically have a 6-hour limit
            time_limit = datetime.timedelta(hours=6)
            remaining_time = time_limit - uptime if uptime < time_limit else datetime.timedelta(0)
            
            # Get workflow logs URL
            logs_url = run.logs_url
            
            # Try to extract RDP info from the logs or job output
            rdp_info = get_rdp_info(run.id)
            
            runs_data.append({
                'id': run.id,
                'name': run.name or run.workflow_id,
                'status': run.status,
                'conclusion': run.conclusion,
                'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'uptime': str(uptime).split('.')[0],  # Remove microseconds
                'remaining_time': str(remaining_time).split('.')[0],  # Remove microseconds
                'html_url': run.html_url,
                'logs_url': logs_url,
                'rdp_info': rdp_info
            })
        
        return runs_data
    except Exception as e:
        print(f"Error fetching workflow runs: {e}")
        return []

def get_rdp_info(run_id):
    """Extract RDP connection information from workflow logs"""
    g = get_github_api()
    if not g:
        return {}
    
    try:
        repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
        
        # Get the jobs for this run
        jobs_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(jobs_url, headers=headers)
        
        if response.status_code != 200:
            return {}
        
        jobs_data = response.json()
        
        # Look for RDP information in job steps output
        rdp_info = {
            'ip': None,
            'username': None,
            'password': None
        }
        
        for job in jobs_data.get('jobs', []):
            for step in job.get('steps', []):
                output = step.get('output', {}).get('text', '')
                
                # Check if output contains RDP info
                if 'IP:' in output:
                    ip_line = [line for line in output.split('\n') if 'IP:' in line]
                    if ip_line:
                        rdp_info['ip'] = ip_line[0].replace('IP:', '').strip()
                
                if 'Username:' in output:
                    username_line = [line for line in output.split('\n') if 'Username:' in line]
                    if username_line:
                        rdp_info['username'] = username_line[0].replace('Username:', '').strip()
                
                if 'Password:' in output:
                    password_line = [line for line in output.split('\n') if 'Password:' in line]
                    if password_line:
                        rdp_info['password'] = password_line[0].replace('Password:', '').strip()
        
        return rdp_info
    except Exception as e:
        print(f"Error getting RDP info: {e}")
        return {}

@app.route('/')
def index():
    """Homepage - redirects to dashboard if logged in, otherwise to login page"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD, password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard page"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', 
                          repo_owner=REPO_OWNER,
                          repo_name=REPO_NAME)

@app.route('/api/workflow-runs')
def api_workflow_runs():
    """API endpoint to get workflow runs data"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    limit = request.args.get('limit', 10, type=int)
    runs = get_workflow_runs(limit)
    return jsonify(runs)

@app.route('/api/create-workflow-run', methods=['POST'])
def api_create_workflow_run():
    """API endpoint to trigger a new workflow run"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    workflow_id = request.form.get('workflow_id')
    if not workflow_id:
        return jsonify({'error': 'Workflow ID is required'}), 400
    
    g = get_github_api()
    if not g:
        return jsonify({'error': 'GitHub API not configured'}), 500
    
    try:
        repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
        workflow = repo.get_workflow(workflow_id)
        run = workflow.create_dispatch('main')
        return jsonify({'success': True, 'message': 'Workflow triggered successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 