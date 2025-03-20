# Auto Commit App

A full-stack application with a React frontend and Flask backend that automates GitHub commits on a schedule.

## Project Structure

- **frontend/**: React frontend built with TypeScript, Vite, and Tailwind CSS
- **server/**: Flask backend API

## Local Development Setup

### Prerequisites

- Node.js (v16+)
- Python (v3.8+)
- Git

### Backend Setup

1. Navigate to the server directory:
   ```bash
   cd server
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file by copying `.env.example`:
   ```bash
   cp .env.example .env
   ```

6. Edit the `.env` file with your GitHub OAuth credentials and other configuration.

7. Run the Flask server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file by copying `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

## GitHub Setup

### Creating a GitHub Repository

1. Initialize a Git repository (if not already done):
   ```bash
   git init
   ```

2. Add all files to Git, excluding those in `.gitignore`:
   ```bash
   git add .
   ```

3. Commit the changes:
   ```bash
   git commit -m "Initial commit"
   ```

4. Create a new repository on GitHub through the web interface.

5. Link your local repository to the GitHub repository:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo-name.git
   ```

6. Push your code to GitHub:
   ```bash
   git push -u origin main
   ```

### Protecting Sensitive Information

1. Ensure all sensitive information is in `.env` files
2. Verify that `.env` files are listed in `.gitignore`
3. Use environment variables for all sensitive information
4. Never commit `.env` files to the repository

## Deployment Options

### Option 1: Deploying to Render

#### Prerequisites

1. Create a Render account at [render.com](https://render.com)
2. Connect your GitHub account to Render

#### Backend Deployment Steps

1. In the Render dashboard, click "New" and select "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - Name: auto-commit-backend (or your preferred name)
   - Root Directory: server
   - Environment: Python
   - Build Command: `pip install -r requirements-deploy.txt`
   - Start Command: `bash ./start.sh`
   - Select the appropriate plan (Free tier is available)

   > **Important**: If you encounter the "gunicorn: command not found" error, make sure you're using the `start.sh` script as your start command, which ensures gunicorn is properly installed.

4. Add environment variables:
   - Click on "Environment" tab
   - Add all variables from your `.env` file:
     - FLASK_SECRET_KEY
     - GITHUB_CLIENT_ID
     - GITHUB_CLIENT_SECRET
     - GITHUB_REDIRECT_URI (use your Render URL: https://your-backend.onrender.com/api/github/callback)
     - GITHUB_WEBHOOK_SECRET
     - WEBHOOK_URL (use your Render URL: https://your-backend.onrender.com/api/github/webhook)
     - FRONTEND_URL (your frontend URL)
     - ALLOWED_ORIGINS (comma-separated list including your frontend URL)

5. Click "Create Web Service"

#### Frontend Deployment Steps

1. In the Render dashboard, click "New" and select "Static Site"
2. Connect your GitHub repository
3. Configure the service:
   - Name: auto-commit-frontend (or your preferred name)
   - Root Directory: frontend
   - Build Command: `npm install && npm run build`
   - Publish Directory: dist

4. Add environment variables:
   - VITE_API_BASE_URL (your backend Render URL: https://your-backend.onrender.com)

5. Click "Create Static Site"

### Option 2: Deploying to Vercel

#### Prerequisites

1. Create a Vercel account at [vercel.com](https://vercel.com)
2. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```

#### Deployment Steps

1. Login to Vercel:
   ```bash
   vercel login
   ```

2. Deploy the project:
   ```bash
   vercel
   ```

3. Follow the prompts to configure your project.

#### Setting Environment Variables in Vercel

1. Go to your project on the Vercel dashboard
2. Navigate to Settings > Environment Variables
3. Add all the environment variables from your `.env` files
4. Make sure to add:
   - All GitHub OAuth credentials
   - Flask secret key
   - Frontend URL (your Vercel deployment URL)
   - Allowed origins (your Vercel deployment URL)

### Configuring GitHub OAuth for Production

1. Go to your GitHub OAuth application settings
2. Update the callback URL to your Vercel deployment URL:
   ```
   https://your-app.vercel.app/api/github/callback
   ```

## Troubleshooting

- If you encounter CORS issues, make sure your `ALLOWED_ORIGINS` environment variable includes your frontend URL
- For GitHub OAuth issues, verify that your callback URLs are correctly configured
- Check Vercel logs for any server-side errors

## Security Considerations

- Never store tokens directly in your code
- Use environment variables for all sensitive information
- Consider implementing token encryption for additional security
- Regularly rotate your GitHub tokens and secrets# GitHub Auto-Commit App

An application that automatically creates and maintains a GitHub repository with daily commits.

## Features

- GitHub OAuth authentication
- Automatic repository creation
- Configurable daily commits (randomly between 1-10 commits per day)
- Random commit scheduling during business hours
- Modern React frontend with TypeScript and Vite
- Event-driven architecture for reliable scheduling

## Technology Stack

### Backend
- Flask
- APScheduler for task scheduling
- GitHub API for repository management and commits

### Frontend
- React with TypeScript
- Vite for fast development
- React Router for navigation
- Tailwind CSS for styling
- Axios for API communication

## Architecture Overview

The application follows an event-driven architecture:

1. **Authentication Flow**:
   - User authenticates via GitHub OAuth
   - Backend stores access token in session
   - Frontend redirects to dashboard

2. **Repository Creation**:
   - User initiates repository creation from dashboard
   - Backend creates repository using GitHub API
   - Backend schedules daily commit jobs

3. **Commit Scheduling**:
   - At midnight each day, a random number (1-10) of commits is scheduled
   - Commits are distributed randomly throughout business hours (9 AM - 5 PM)
   - Each commit updates the README.md file with a timestamp

4. **User Interface**:
   - Dashboard shows repository status and scheduled commits
   - Real-time updates when commits are scheduled or completed

## Getting Started

Follow the setup instructions in the project documentation:

1. Set up the Flask backend
2. Configure GitHub OAuth
3. Start the React frontend
4. Connect your GitHub account

## Security Considerations

- OAuth tokens are stored in server-side sessions only
- Environment variables are used for sensitive information
- CORS is configured for enhanced security
- HTTPS is recommended for production deployment

## Development

See the setup instructions for detailed development setup steps.