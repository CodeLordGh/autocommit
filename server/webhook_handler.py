"""
Webhook Handler Module

This module handles GitHub webhook events.
"""
import hmac
import hashlib
from typing import Dict, Any, Optional
import database as db

class WebhookHandler:
    """Handles GitHub webhook events"""
    
    def __init__(self, webhook_secret: str = ""):
        """
        Initialize with webhook secret
        
        Args:
            webhook_secret: Secret for webhook signature verification
        """
        self.webhook_secret = webhook_secret
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify the GitHub webhook signature
        
        Args:
            payload: Raw request payload
            signature: Signature from X-Hub-Signature-256 header
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.webhook_secret or not signature:
            print("Missing webhook secret or signature")
            return False
        
        # Compute expected signature
        signature_parts = signature.split("=")
        if len(signature_parts) != 2 or signature_parts[0] != "sha256":
            print(f"Invalid signature format: {signature}")
            return False
        
        expected_signature = signature_parts[1]
        computed_signature = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        is_valid = hmac.compare_digest(computed_signature, expected_signature)
        if is_valid:
            print("Webhook signature verified successfully")
        else:
            print(f"Webhook signature verification failed. Expected: {expected_signature}, Computed: {computed_signature}")
        
        return is_valid
    
    def handle_push_event(self, payload: Dict[str, Any]) -> bool:
        """
        Handle GitHub push event

        Args:
            payload: Webhook payload

        Returns:
            True if handled successfully, False otherwise
        """
        try:
            print("\n=== GitHub Webhook: Push Event ===")
            ref = payload.get('ref', 'unknown ref')
            print(f"Branch/Ref: {ref}")

            # Extract repository information
            repository = payload.get("repository", {})
            repo_name = repository.get("name")
            repo_owner = repository.get("owner", {}).get("name")

            if not repo_name or not repo_owner:
                print(f"ERROR: Missing repository information: name={repo_name}, owner={repo_owner}")
                print("Payload keys available: " + ", ".join(payload.keys()))
                return False

            print(f"Repository: {repo_owner}/{repo_name}")

            # Extract commit information
            commits = payload.get("commits", [])
            print(f"Commits in push: {len(commits)}")

            if len(commits) == 0:
                print("WARNING: No commits found in push event")
                print("This might be a branch creation or deletion event")
                return True

            # Process each commit
            for i, commit in enumerate(commits):
                commit_id = commit.get("id")
                commit_message = commit.get("message", "").strip()
                commit_url = commit.get("url")
                commit_author = commit.get("author", {}).get("name", "Unknown")
                commit_timestamp = commit.get("timestamp", "Unknown time")

                print(f"\nCommit {i+1}/{len(commits)}:")
                print(f"  SHA: {commit_id[:10]}...")
                print(f"  Author: {commit_author}")
                print(f"  Time: {commit_timestamp}")
                print(f"  Message: {commit_message[:50]}..." if len(commit_message) > 50 else f"  Message: {commit_message}")

                if not commit_id or not commit_url:
                    print(f"  ERROR: Missing required commit data: id={commit_id}, url={commit_url}")
                    continue

                # Record in database
                success = db.record_commit(
                    username=repo_owner,
                    repo_name=repo_name,
                    commit_sha=commit_id,
                    commit_message=commit_message or "No commit message",
                    commit_url=commit_url
                )

                if success:
                    print(f"  ✓ Successfully recorded in database")
                else:
                    print(f"  ✗ Failed to record in database")

            print("=== End of Push Event Processing ===\n")
            return True

        except Exception as e:
            print(f"\n=== ERROR in Push Event Handler ===")
            print(f"Exception: {str(e)}")
            print(f"Exception type: {type(e).__name__}")

            # Try to print some payload information for debugging
            try:
                if payload:
                    print("Payload keys: " + ", ".join(payload.keys()))
                    if "repository" in payload:
                        repo = payload["repository"]
                        print(f"Repository: {repo.get('full_name', 'unknown')}")
                else:
                    print("Payload is empty or None")
            except:
                print("Could not extract payload information")

            print("=== End of Error Report ===\n")
            return False