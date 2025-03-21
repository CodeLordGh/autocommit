"""
Main Flask Application

This is the main entry point for the Auto Commit App backend.
"""
from flask import Flask, request, redirect, session, jsonify
from flask_cors import CORS
import os
import json
import requests
import datetime
from dotenv import load_dotenv
import database as db
from github_client import GitHubClient
from scheduler import commit_scheduler
from webhook_handler import WebhookHandler

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# Get allowed origins from environment or use default
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
CORS(app, supports_credentials=True, origins=ALLOWED_ORIGINS, allow_headers=["Content-Type", "Authorization"])
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

# Configure session to be more secure and work with CORS
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Use 'None' for cross-site requests with HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)  # Session lasts 7 days

@app.route('/')
def root():
    """Root endpoint to check if server is available"""
    return jsonify({
        "status": "success",
        "message": "Server available",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/test')
def test_page():
    """Serve the test HTML page"""
    return app.send_static_file('test.html')

# We've removed the excessive logging here

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.environ.get("GITHUB_REDIRECT_URI", "http://localhost:5000/api/github/callback")
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"

# GitHub webhook secret
GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "http://localhost:5000/api/github/webhook")

# Scheduler is initialized in scheduler.py

# Initialize webhook handler
webhook_handler = WebhookHandler(GITHUB_WEBHOOK_SECRET)

# Initialize database on startup
db.init_db()

@app.route("/api/github/login")
def github_login():
    """Redirect to GitHub OAuth login"""
    print("Redirecting to GitHub OAuth login")
    scope = "repo user"
    return redirect(f"{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope={scope}")

@app.route("/api/github/callback")
def github_callback():
    """Handle GitHub OAuth callback"""
    code = request.args.get("code")
    print(f"Received GitHub OAuth callback with code: {code[:10] if code else 'None'}...")

    try:
        # Exchange code for access token
        response = requests.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI
            },
            headers={"Accept": "application/json"}
        )

        data = response.json()
        if "access_token" not in data:
            print(f"Failed to get access token: {json.dumps(data, indent=2)}")
            return jsonify({"error": "Failed to get access token"}), 400

        token = data["access_token"]

        # Create GitHub client
        github_client = GitHubClient(token)

        # Get user info
        user_data = github_client.get_user_info()

        if "login" not in user_data:
            print(f"Failed to get user info: {json.dumps(user_data, indent=2)}")
            return jsonify({"error": "Failed to get user info"}), 400

        username = user_data["login"]

        # Store in session
        session["github_token"] = token
        session["github_username"] = username

        # Store token in database
        db.store_user_token(username, token)

        # Check if user already has a repository and restore scheduler if needed
        user_data = db.get_user_token(username)
        if user_data and user_data.get("repo_name"):
            commit_scheduler.setup_midnight_scheduler(username, token, user_data["repo_name"])

        return redirect("http://localhost:5173/dashboard")

    except Exception as e:
        print(f"Error during GitHub callback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/user")
def get_user():
    """Get current authenticated user info with app-specific repository details"""
    if "github_token" not in session:
        return jsonify({"authenticated": False}), 401

    username = session.get("github_username")

    # Check if user has a repository created through our platform
    user_data = db.get_user_token(username)
    platform_repo = user_data["repo_name"] if user_data and user_data["repo_name"] else None

    return jsonify({
        "authenticated": True,
        "username": username,
        "hasRepository": bool(platform_repo),
        "repositoryName": platform_repo
    })

@app.route("/api/create-repository", methods=["POST"])
def create_repository():
    """Create a new GitHub repository"""
    # Check authentication
    if "github_token" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    token = session["github_token"]
    username = session["github_username"]

    # Get repository details from request
    data = request.json
    if not data:
        return jsonify({"error": "Missing repository data"}), 400

    repo_name = data.get("repoName", "auto-commit-app")
    repo_description = data.get("description", "Repository for automated commits")

    try:
        # Create GitHub client
        github_client = GitHubClient(token)

        # Create repository
        repo_data, status_code = github_client.create_repository(
            name=repo_name,
            description=repo_description
        )

        # Handle repository name conflict
        if (status_code in [400, 422]) and repo_data.get("name_conflict"):
            print(f"Handling repository name conflict with status code {status_code}")
            return jsonify({
                "error": repo_data.get("user_message", f"Repository '{repo_name}' already exists"),
                "name_conflict": True,
                "suggested_names": [
                    f"{repo_name}-{username}",
                    f"{repo_name}-{datetime.datetime.now().strftime('%Y%m%d')}",
                    f"{repo_name}-project"
                ]
            }), 409  # Using 409 Conflict status code

        # Handle other errors
        if status_code not in [201, 200]:
            error_message = "Failed to create repository"

            if isinstance(repo_data, dict) and "message" in repo_data:
                error_message = repo_data["message"]

            print(f"Repository creation failed with status {status_code}: {error_message}")
            print(f"Detailed error data: {json.dumps(repo_data, indent=2)}")

            # Check if this might be a name conflict that wasn't caught earlier
            if isinstance(repo_data, dict) and "message" in repo_data:
                if "already exists" in repo_data["message"].lower():
                    print("Detected possible name conflict from error message")
                    return jsonify({
                        "error": f"Repository '{repo_name}' already exists. Please choose a different name.",
                        "name_conflict": True,
                        "suggested_names": [
                            f"{repo_name}-{username}",
                            f"{repo_name}-{datetime.datetime.now().strftime('%Y%m%d')}",
                            f"{repo_name}-project"
                        ]
                    }), 409

            return jsonify({
                "error": error_message,
                "details": repo_data
            }), status_code

        # Store repository name in database
        db.store_user_token(username, token, repo_name)

        # Set up webhook
        github_client.setup_webhook(
            username=username,
            repo_name=repo_name,
            webhook_url=WEBHOOK_URL,
            secret=GITHUB_WEBHOOK_SECRET
        )

        # Set up commit scheduling
        print(f"Setting up daily commit scheduling for {username}/{repo_name}")
        commit_scheduler.setup_daily_commits(username, token, repo_name)

        # Make initial commit
        commit_message = "Initial commit from Auto Commit App"
        commit_data, success, commit_sha = github_client.make_commit(
            username=username,
            repo_name=repo_name,
            commit_message=commit_message
        )

        if success:
            # Record the commit
            commit_url = f"https://github.com/{username}/{repo_name}/commit/{commit_sha}"
            db.record_commit(username, repo_name, commit_sha, commit_message, commit_url)

        return jsonify({
            "success": True,
            "repo": {
                "name": repo_data["name"],
                "html_url": repo_data["html_url"],
                "description": repo_data["description"]
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/github/webhook", methods=["POST"])
def github_webhook():
    """Handle GitHub webhooks"""
    # Verify webhook signature
    if GITHUB_WEBHOOK_SECRET:
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not webhook_handler.verify_signature(request.data, signature):
            return jsonify({"error": "Invalid signature"}), 401

    event_type = request.headers.get("X-GitHub-Event")

    if event_type == "push":
        if webhook_handler.handle_push_event(request.json):
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Failed to process push event"}), 500

    return jsonify({"success": True})

@app.route("/api/commits")
def get_commits():
    """Get commit history for the user's repository"""
    if "github_username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    username = session["github_username"]
    user_data = db.get_user_token(username)

    if not user_data or not user_data["repo_name"]:
        return jsonify({"error": "No repository found"}), 404

    repo_name = user_data["repo_name"]
    commits = db.get_user_commits(username, repo_name)

    return jsonify(commits)

@app.route("/api/github/status")
def get_status():
    """Get the status of scheduled commits and commit history"""
    if "github_token" not in session or "github_username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    username = session["github_username"]

    # Check database for the repository
    user_data = db.get_user_token(username)
    platform_repo = user_data["repo_name"] if user_data and user_data["repo_name"] else None

    if not platform_repo:
        return jsonify({
            "active": False,
            "hasRepository": False,
            "repo_name": None,
            "scheduled_commits": 0,
            "total_commits": 0,
            "next_commit": {
                "has_scheduled_commits": False,
                "formatted_time": None,
                "formatted_countdown": None
            }
        })

    # Ensure scheduler is active
    scheduled_commits = commit_scheduler.get_scheduled_commits_count(username)
    if scheduled_commits == 0 and user_data and user_data["token"]:
        commit_scheduler.setup_midnight_scheduler(username, user_data["token"], platform_repo)
        scheduled_commits = commit_scheduler.get_scheduled_commits_count(username)

    # Get total commits
    total_commits = len(db.get_user_commits(username, platform_repo, limit=None))

    # Get next commit time information
    next_commit_info = commit_scheduler.get_next_commit_time(username)

    print(f"Next commit info for {username}: {next_commit_info}")

    response_data = {
        "active": True,
        "hasRepository": True,
        "repo_name": platform_repo,
        "scheduled_commits": scheduled_commits,
        "total_commits": total_commits,
        "next_commit": {
            "has_scheduled_commits": next_commit_info["has_scheduled_commits"],
            "formatted_time": next_commit_info["formatted_time"],
            "formatted_countdown": next_commit_info["formatted_countdown"],
            "seconds_until_next": next_commit_info["seconds_until_next"]
        }
    }

    print(f"Returning status response: {response_data}")

    return jsonify(response_data)

@app.route("/api/logout", methods=["POST"])
def logout():
    """Logout and clear session"""
    session.clear()
    return jsonify({"success": True})

@app.route("/api/debug/session")
def debug_session():
    """Debug endpoint to check session data"""
    return jsonify({
        "authenticated": "github_token" in session,
        "username": session.get("github_username", None),
        "has_token": "github_token" in session
    })

def initialize_app():
    """Initialize the application"""
    # Initialize database
    try:
        db.init_db()

        # Verify database is working by checking if we can query it
        users = db.get_users_with_repositories()
    except Exception as e:
        print(f"ERROR initializing database: {str(e)}")
        # We continue anyway to allow debugging

    # Restore schedulers for all users
    try:
        # Try to restore schedulers
        commit_scheduler.restore_schedulers()
    except Exception as e:
        print(f"Error restoring schedulers: {str(e)}")
        try:
            # Import the clear_job_store function
            from scheduler import clear_job_store

            # Clear the job store
            if clear_job_store():
                # Try to restore schedulers again
                commit_scheduler.restore_schedulers()
            else:
                print("Failed to clear job store")
        except Exception as e2:
            print(f"Error during recovery attempt: {str(e2)}")
            # Continue despite errors

# Initialize the app when this module is imported
initialize_app()

if __name__ == "__main__":
    # Only run the development server when this file is executed directly
    app.run(debug=True, port=5000)