# Auto Commit App Backend

This is the backend for the Auto Commit App, which automates GitHub commits on a schedule.

## Modular Structure

The backend is organized into the following modules:

- **app.py**: Main Flask application with API routes
- **database.py**: Database operations for storing user data and commits
- **github_client.py**: Client for interacting with the GitHub API
- **scheduler.py**: Handles scheduling of automated commits
- **webhook_handler.py**: Processes GitHub webhook events

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file with the following variables:
   ```
   FLASK_SECRET_KEY=your_secret_key
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   GITHUB_REDIRECT_URI=http://localhost:5000/api/github/callback
   GITHUB_WEBHOOK_SECRET=your_webhook_secret
   WEBHOOK_URL=http://localhost:5000/api/github/webhook
   ```

3. Run the application:
   ```
   python app.py
   ```

## API Endpoints

- **GET /api/github/login**: Redirect to GitHub OAuth login
- **GET /api/github/callback**: Handle GitHub OAuth callback
- **GET /api/user**: Get current authenticated user info
- **POST /api/create-repository**: Create a new GitHub repository
- **GET /api/commits**: Get commit history for the user's repository
- **GET /api/github/status**: Get the status of scheduled commits
- **POST /api/logout**: Logout and clear session
- **POST /api/github/webhook**: Handle GitHub webhooks

## Debugging

The application includes detailed logging to help diagnose issues. All GitHub API requests and responses are logged, including error details.