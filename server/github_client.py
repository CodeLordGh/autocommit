"""
GitHub API Client Module

This module handles all interactions with the GitHub API.
"""
import requests
import json
import datetime
import os
from typing import Dict, Any, Optional, List, Tuple

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"

class GitHubClient:
    """Client for interacting with GitHub API"""
    
    def __init__(self, token: str):
        """Initialize with GitHub token"""
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Tuple[Dict, int]:
        """
        Make a request to GitHub API with detailed error logging

        Args:
            method: HTTP method (GET, POST, PATCH, etc.)
            endpoint: API endpoint (without base URL)
            data: Request data for POST/PATCH requests

        Returns:
            Tuple of (response_data, status_code)
        """
        url = f"{GITHUB_API_URL}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data
            )

            status_code = response.status_code

            try:
                response_data = response.json()
            except ValueError:
                response_data = {"text": response.text}

            return response_data, status_code

        except Exception as e:
            return {"error": str(e), "error_type": type(e).__name__}, 500
    
    def get_user_info(self) -> Dict:
        """Get authenticated user information"""
        data, status_code = self._make_request("GET", "/user")
        return data
    
    def create_repository(self, name: str, description: str = "", private: bool = False) -> Tuple[Dict, int]:
        """
        Create a new GitHub repository

        Args:
            name: Repository name
            description: Repository description
            private: Whether the repository is private

        Returns:
            Tuple of (repository_data, status_code)
        """
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True  # Initialize with README
        }

        response_data, status_code = self._make_request("POST", "/user/repos", data)

        # Debug information
        print(f"Repository creation response status: {status_code}")
        print(f"Repository creation response data: {json.dumps(response_data, indent=2)}")

        # Check for various error conditions that might indicate name conflict
        if status_code in [400, 422]:
            # Check for the "already exists" error
            if isinstance(response_data, dict):
                # Debug the error structure
                print(f"Error structure: {json.dumps(response_data, indent=2)}")

                # Check for different error formats
                error_message = response_data.get("message", "").lower()

                # Check for "already exists" in the message
                if "already exists" in error_message or "name already exists" in error_message:
                    print(f"Detected name conflict from error message: {error_message}")
                    response_data["name_conflict"] = True
                    response_data["user_message"] = f"A repository named '{name}' already exists. Please choose a different name."

                # Also check the errors array format
                if "errors" in response_data and isinstance(response_data["errors"], list):
                    for error in response_data["errors"]:
                        if (error.get("code") == "already_exists" and error.get("resource") == "Repository") or \
                           (error.get("message", "").lower().find("already exists") >= 0):
                            # This is a repository name conflict
                            print(f"Detected name conflict from errors array: {error}")
                            response_data["name_conflict"] = True
                            response_data["user_message"] = f"A repository named '{name}' already exists. Please choose a different name."
                            break

        return response_data, status_code
    
    def setup_webhook(self, username: str, repo_name: str, webhook_url: str, 
                     secret: Optional[str] = None) -> Tuple[Dict, int]:
        """
        Set up a webhook for a repository
        
        Args:
            username: GitHub username
            repo_name: Repository name
            webhook_url: URL to receive webhook events
            secret: Secret for webhook signature verification
            
        Returns:
            Tuple of (webhook_data, status_code)
        """
        config = {
            "url": webhook_url,
            "content_type": "json"
        }
        
        if secret:
            config["secret"] = secret
            
        data = {
            "name": "web",
            "active": True,
            "events": ["push"],
            "config": config
        }
        
        return self._make_request(
            "POST", 
            f"/repos/{username}/{repo_name}/hooks",
            data
        )
    
    def make_commit(self, username: str, repo_name: str, commit_message: str) -> Tuple[Dict, bool, str]:
        """
        Make a commit to update README.md in a repository
        
        Args:
            username: GitHub username
            repo_name: Repository name
            commit_message: Commit message
            
        Returns:
            Tuple of (commit_data, success, commit_sha)
        """
        try:
            # Get repository info to find default branch
            repo_data, status_code = self._make_request(
                "GET", 
                f"/repos/{username}/{repo_name}"
            )
            
            if status_code != 200:
                return repo_data, False, ""
                
            default_branch = repo_data["default_branch"]
            
            # Get the reference to HEAD
            ref_data, status_code = self._make_request(
                "GET",
                f"/repos/{username}/{repo_name}/git/refs/heads/{default_branch}"
            )
            
            if status_code != 200:
                return ref_data, False, ""
                
            head_sha = ref_data["object"]["sha"]
            
            # Get the commit that HEAD points to
            commit_data, status_code = self._make_request(
                "GET",
                f"/repos/{username}/{repo_name}/git/commits/{head_sha}"
            )
            
            if status_code != 200:
                return commit_data, False, ""
                
            tree_sha = commit_data["tree"]["sha"]
            
            # Create a new blob with updated content
            date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_content = f"# KCommit\n\nThis repository is maintained by the Auto Commit App.\n\nLast updated: {date_str}"
            
            blob_data, status_code = self._make_request(
                "POST",
                f"/repos/{username}/{repo_name}/git/blobs",
                {
                    "content": new_content,
                    "encoding": "utf-8"
                }
            )
            
            if status_code != 201:
                return blob_data, False, ""
                
            blob_sha = blob_data["sha"]
            
            # Create a new tree
            tree_data, status_code = self._make_request(
                "POST",
                f"/repos/{username}/{repo_name}/git/trees",
                {
                    "base_tree": tree_sha,
                    "tree": [
                        {
                            "path": "README.md",
                            "mode": "100644",
                            "type": "blob",
                            "sha": blob_sha
                        }
                    ]
                }
            )
            
            if status_code != 201:
                return tree_data, False, ""
                
            new_tree_sha = tree_data["sha"]
            
            # Create a new commit
            new_commit_data, status_code = self._make_request(
                "POST",
                f"/repos/{username}/{repo_name}/git/commits",
                {
                    "message": commit_message,
                    "tree": new_tree_sha,
                    "parents": [head_sha]
                }
            )
            
            if status_code != 201:
                return new_commit_data, False, ""
                
            new_commit_sha = new_commit_data["sha"]
            
            # Update the reference
            update_ref_data, status_code = self._make_request(
                "PATCH",
                f"/repos/{username}/{repo_name}/git/refs/heads/{default_branch}",
                {
                    "sha": new_commit_sha,
                    "force": False
                }
            )
            
            if status_code != 200:
                return update_ref_data, False, ""
                
            return new_commit_data, True, new_commit_sha
            
        except Exception as e:
            print(f"Exception during commit creation: {str(e)}")
            return {"error": str(e)}, False, ""