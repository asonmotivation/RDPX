# RDP Dashboard

A dark-themed, user-friendly dashboard to monitor and control your free RDP instances created with GitHub Actions.

![RDP Dashboard Screenshot](https://via.placeholder.com/800x450?text=RDP+Dashboard)

## Features

- 🌑 Dark theme UI for comfortable viewing
- 🔍 Real-time monitoring of RDP instances
- ⏱️ Uptime tracking and remaining time calculation
- 🔑 Easily view RDP connection details (IP, username, password)
- 🚀 Create new RDP instances directly from the dashboard
- 📊 Monitor workflow status and logs
- 🔐 Secure login system

## Deployment on Vercel

### Prerequisites

1. GitHub account with a personal access token that has `repo` and `workflow` permissions
2. Vercel account
3. A fork of the RDP GitHub repository

### Setup Steps

1. **Fork or clone this dashboard repository**

2. **Create environment variables for Vercel deployment**

   Copy the `.env.example` file to a new file named `.env` and fill in your details:
   ```
   SECRET_KEY=your-generated-secret-key
   GITHUB_TOKEN=your-github-personal-access-token
   REPO_OWNER=your-github-username
   REPO_NAME=your-rdp-repo-name
   ADMIN_USERNAME=your-preferred-username
   ADMIN_PASSWORD_HASH=your-password-hash
   ```

   To generate a password hash, you can use this Python code:
   ```python
   from werkzeug.security import generate_password_hash
   print(generate_password_hash("your-password"))
   ```

3. **Deploy to Vercel**

   - Install Vercel CLI: `npm i -g vercel`
   - Login to Vercel: `vercel login`
   - Deploy: `vercel --prod`
   
   Alternatively, you can deploy through the Vercel web interface:
   - Go to [vercel.com](https://vercel.com)
   - Create a new project and import your repository
   - Configure your environment variables
   - Deploy

4. **Access your dashboard**

   Once deployed, your dashboard will be available at the Vercel-provided URL.
   Log in with your specified admin credentials.

## Local Development

1. Clone the repository
2. Create a `.env` file based on `.env.example`
3. Install requirements: `pip install -r requirements.txt`
4. Run the application: `python app.py`
5. Access at `http://localhost:5000`

## Security Notes

- Change the default admin username and password for production use
- Store your GitHub token securely
- The RDP connection details are visible to anyone with access to your dashboard
- Consider implementing additional security measures for production use

## License

MIT

---

*Made with ❤️ for the RDP community* 