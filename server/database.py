"""
Database Module

This module handles all database operations.
"""
import sqlite3
import os
import datetime
import json
from typing import Dict, List, Any, Optional, Union

# Database initialization
DB_PATH = os.path.join(os.path.dirname(__file__), 'commits.db')

def init_db():
    """Initialize the SQLite database"""
    # Ensure the directory exists
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create commits table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS commits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            repo_name TEXT NOT NULL,
            commit_sha TEXT NOT NULL,
            commit_message TEXT NOT NULL,
            commit_url TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')

        # Create users table to store tokens securely
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            repo_name TEXT,
            webhook_secret TEXT
        )
        ''')

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

def record_commit(username: str, repo_name: str, commit_sha: str, commit_message: str, commit_url: str) -> bool:
    """
    Record a commit to the database
    
    Args:
        username: GitHub username
        repo_name: Repository name
        commit_sha: Commit SHA
        commit_message: Commit message
        commit_url: URL to the commit on GitHub
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Recording commit {commit_sha[:7]} for {username}/{repo_name}")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        timestamp = datetime.datetime.now().isoformat()
        
        cursor.execute(
            '''INSERT INTO commits (username, repo_name, commit_sha, commit_message, commit_url, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (username, repo_name, commit_sha, commit_message, commit_url, timestamp)
        )
        
        conn.commit()
        conn.close()
        
        print(f"Successfully recorded commit {commit_sha[:7]}")
        return True
        
    except Exception as e:
        print(f"Error recording commit: {str(e)}")
        return False

def get_user_commits(username: str, repo_name: str, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
    """
    Get commit history for a user's repository
    
    Args:
        username: GitHub username
        repo_name: Repository name
        limit: Maximum number of commits to return, None for all
        
    Returns:
        List of commit dictionaries
    """
    try:
        print(f"Getting commits for {username}/{repo_name} with limit {limit}")
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Return results as dictionaries
        cursor = conn.cursor()
        
        if limit:
            cursor.execute(
                '''SELECT * FROM commits 
                   WHERE username = ? AND repo_name = ? 
                   ORDER BY timestamp DESC LIMIT ?''',
                (username, repo_name, limit)
            )
        else:
            cursor.execute(
                '''SELECT * FROM commits 
                   WHERE username = ? AND repo_name = ? 
                   ORDER BY timestamp DESC''',
                (username, repo_name)
            )
        
        commits = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        print(f"Found {len(commits)} commits for {username}/{repo_name}")
        return commits
        
    except Exception as e:
        print(f"Error getting user commits: {str(e)}")
        return []

def store_user_token(username: str, token: str, repo_name: Optional[str] = None, webhook_secret: Optional[str] = None) -> bool:
    """
    Store user token securely

    Args:
        username: GitHub username
        token: GitHub token
        repo_name: Repository name (optional)
        webhook_secret: Webhook secret (optional)

    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check if user already exists and has a repository
        cursor.execute('SELECT repo_name FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()

        if existing_user and existing_user['repo_name'] and not repo_name:
            # User exists and has a repository, but no new repo_name provided
            # Keep the existing repository information
            cursor.execute(
                '''UPDATE users SET token = ? WHERE username = ?''',
                (token, username)
            )
        else:
            # Either user doesn't exist, or we're explicitly setting a new repo_name
            cursor.execute(
                '''INSERT OR REPLACE INTO users (username, token, repo_name, webhook_secret)
                   VALUES (?, ?, ?, ?)''',
                (username, token, repo_name, webhook_secret)
            )

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error storing user token: {str(e)}")
        return False

def get_user_token(username: str) -> Optional[Dict[str, Any]]:
    """
    Get stored token for a user

    Args:
        username: GitHub username

    Returns:
        Dictionary with token, repo_name, and webhook_secret, or None if not found
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT token, repo_name, webhook_secret FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return dict(user_data)
        else:
            return None

    except Exception as e:
        print(f"Error getting user token: {str(e)}")
        return None

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """
    Get user information from the database
    
    Args:
        username: GitHub username
        
    Returns:
        Dictionary with user information, or None if not found
    """
    try:
        print(f"Getting user information for {username}")
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT username, token, repo_name FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            print(f"Found user information for {username}")
            return dict(user_data)
        else:
            print(f"No user information found for {username}")
            return None
        
    except Exception as e:
        print(f"Error getting user information: {str(e)}")
        return None

def store_webhook_secret(username: str, repo_name: str, webhook_secret: str) -> bool:
    """
    Store webhook secret for a repository
    
    Args:
        username: GitHub username
        repo_name: Repository name
        webhook_secret: Webhook secret
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Storing webhook secret for {username}/{repo_name}")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            '''UPDATE users SET webhook_secret = ? WHERE username = ? AND repo_name = ?''',
            (webhook_secret, username, repo_name)
        )
        
        conn.commit()
        conn.close()
        
        print(f"Successfully stored webhook secret for {username}/{repo_name}")
        return True
        
    except Exception as e:
        print(f"Error storing webhook secret: {str(e)}")
        return False

def get_webhook_secret(username: str, repo_name: str) -> Optional[str]:
    """
    Get webhook secret for a repository
    
    Args:
        username: GitHub username
        repo_name: Repository name
        
    Returns:
        Webhook secret, or None if not found
    """
    try:
        print(f"Getting webhook secret for {username}/{repo_name}")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT webhook_secret FROM users WHERE username = ? AND repo_name = ?', 
                      (username, repo_name))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            print(f"Found webhook secret for {username}/{repo_name}")
            return result[0]
        else:
            print(f"No webhook secret found for {username}/{repo_name}")
            return None
        
    except Exception as e:
        print(f"Error getting webhook secret: {str(e)}")
        return None

def get_users_with_repositories() -> List[Dict[str, Any]]:
    """
    Get all users who have repositories created through the platform
    
    Returns:
        List of user dictionaries with username, token, and repo_name
    """
    try:
        print("Getting all users with repositories")
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT username, token, repo_name FROM users WHERE repo_name IS NOT NULL')
        users = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        print(f"Found {len(users)} users with repositories")
        return users
        
    except Exception as e:
        print(f"Error getting users with repositories: {str(e)}")
        return []