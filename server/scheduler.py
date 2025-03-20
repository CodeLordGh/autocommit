"""
Scheduler Module

This module handles scheduling of commits and other periodic tasks.
"""
import random
import json
import datetime
from typing import Dict, List, Any, Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import database as db
from github_client import GitHubClient

# Store for user jobs
user_jobs = {}

# Define standalone functions for job execution to avoid serialization issues
def make_scheduled_commit(token: str, username: str, repo_name: str) -> None:
    """
    Make a scheduled commit (standalone function)

    Args:
        token: GitHub token
        username: GitHub username
        repo_name: Repository name
    """
    print(f"\n=== Scheduled Commit Execution ===")
    print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"User: {username}")
    print(f"Repository: {repo_name}")

    try:
        commit_message = f"Automated commit at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # Create GitHub client
        github_client = GitHubClient(token)

        # Make the commit
        print(f"Initiating commit with message: {commit_message}")
        commit_data, success, commit_sha = github_client.make_commit(username, repo_name, commit_message)

        if success:
            print(f"✓ Commit successful!")
            print(f"Commit SHA: {commit_sha}")

            # Record the commit in the database
            commit_url = f"https://github.com/{username}/{repo_name}/commit/{commit_sha}"
            db_success = db.record_commit(username, repo_name, commit_sha, commit_message, commit_url)

            if db_success:
                print(f"✓ Commit recorded in database")
            else:
                print(f"✗ Failed to record commit in database")
        else:
            print(f"✗ Commit failed")
            if isinstance(commit_data, dict):
                if "message" in commit_data:
                    print(f"Error message: {commit_data['message']}")
                elif "error" in commit_data:
                    print(f"Error: {commit_data['error']}")
                else:
                    print(f"Error data: {commit_data}")

    except Exception as e:
        print(f"✗ Exception during scheduled commit: {str(e)}")
        print(f"Exception type: {type(e).__name__}")

    print("=== End of Scheduled Commit ===\n")

    # Get the scheduler instance to update next commit information
    from scheduler import commit_scheduler
    # This will ensure the next_commit information is updated for the frontend
    commit_scheduler.update_next_commit_info(username)

def schedule_todays_commits_job(username: str, token: str, repo_name: str) -> None:
    """
    Standalone function to schedule today's commits

    Args:
        username: GitHub username
        token: GitHub token
        repo_name: Repository name
    """
    print(f"Scheduling today's commits for {username}/{repo_name}")

    # Get the scheduler instance
    from scheduler import commit_scheduler

    # Clear existing jobs for this user
    if username in user_jobs:
        for job_id in user_jobs[username]:
            if not job_id.endswith("daily_scheduler"):
                try:
                    commit_scheduler.scheduler.remove_job(job_id)
                    print(f"Removed existing job {job_id}")
                except Exception as e:
                    print(f"Error removing job {job_id}: {str(e)}")

        # Keep only the daily scheduler job
        user_jobs[username] = [job_id for job_id in user_jobs[username]
                              if job_id.endswith("daily_scheduler")]

    # Choose random number of commits for today (1-10)
    # For testing, ensure at least one commit is scheduled in the next few minutes
    num_commits = random.randint(1, 10)
    print(f"Scheduling {num_commits} commits for today")

    # Debug: Force a commit to be scheduled soon for testing
    debug_force_commit = False  # Set to False in production
    if debug_force_commit:
        # Schedule a commit in the next 5 minutes for testing
        now = datetime.datetime.now()
        test_commit_time = now + datetime.timedelta(minutes=5)
        job_id = f"{username}_{repo_name}_test"

        try:
            print(f"DEBUG: Scheduling a test commit at {test_commit_time}")
            commit_scheduler.scheduler.add_job(
                func=make_scheduled_commit,
                trigger="date",
                run_date=test_commit_time,
                id=job_id,
                args=[token, username, repo_name],
                replace_existing=True
            )

            # Add to user_jobs if not already there
            if job_id not in user_jobs.get(username, []):
                user_jobs.setdefault(username, []).append(job_id)

            print(f"DEBUG: Scheduled test commit with job ID {job_id}")
        except Exception as e:
            print(f"DEBUG: Error scheduling test commit: {str(e)}")

    # Get business hours (9 AM to 9 PM)
    now = datetime.datetime.now()
    start_time = datetime.datetime(now.year, now.month, now.day, 9, 0, 0)
    end_time = datetime.datetime(now.year, now.month, now.day, 21, 0, 0)  # 9 PM

    # Always schedule for today, even if it's past business hours
    # This ensures we always have the right number of commits scheduled

    # If it's before 9 AM, start at 9 AM
    effective_start = max(now, start_time)

    # If it's already past 9 PM, schedule for tomorrow
    if now > end_time:
        print("It's past business hours, scheduling for tomorrow's business hours")
        tomorrow = now + datetime.timedelta(days=1)
        start_time = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0, 0)
        end_time = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 21, 0, 0)
        effective_start = start_time

    # Calculate available seconds in the business hours
    available_seconds = (end_time - effective_start).total_seconds()

    # Ensure we have enough time for all commits (at least 60 seconds apart)
    min_time_needed = num_commits * 60  # 60 seconds minimum between commits

    if available_seconds < min_time_needed:
        print(f"Not enough time for {num_commits} commits. Adjusting to fit within business hours.")
        num_commits = max(1, int(available_seconds / 60))
        print(f"Adjusted to {num_commits} commits")

    # Divide the business hours into segments
    segment_seconds = available_seconds / num_commits

    # Schedule the commits at random times within each segment
    current_time = effective_start
    for i in range(num_commits):
        # Calculate the end of this segment
        segment_end = current_time + datetime.timedelta(seconds=segment_seconds)

        # Choose a random time within this segment
        # Ensure at least 60 seconds from the start of the segment
        min_seconds = min(60, int(segment_seconds * 0.1))
        max_seconds = max(min_seconds, int(segment_seconds * 0.9))

        random_seconds = random.randint(min_seconds, max_seconds)
        commit_time = current_time + datetime.timedelta(seconds=random_seconds)

        # Ensure we're still within business hours
        if commit_time > end_time:
            commit_time = end_time - datetime.timedelta(seconds=60)
            print(f"Adjusted commit time to stay within business hours: {commit_time}")

        # Schedule the job
        job_id = f"{username}_{repo_name}_{i}"

        # Check if job already exists in the scheduler
        try:
            commit_scheduler.scheduler.add_job(
                func=make_scheduled_commit,
                trigger="date",
                run_date=commit_time,
                id=job_id,
                args=[token, username, repo_name],
                replace_existing=True  # Replace if job already exists
            )

            # Add to user_jobs if not already there
            if job_id not in user_jobs.get(username, []):
                user_jobs.setdefault(username, []).append(job_id)

            print(f"Scheduled commit at {commit_time} with job ID {job_id}")
        except Exception as e:
            print(f"Error scheduling job {job_id}: {str(e)}")

        # Move to the next segments
        current_time = current_time + datetime.timedelta(seconds=segment_seconds)

class CommitScheduler:
    """Handles scheduling of commits"""

    def __init__(self):
        """Initialize the scheduler"""
        self.scheduler = BackgroundScheduler()

        # Configure the scheduler to use a more robust job store
        # This helps ensure jobs persist even if the application is restarted
        try:
            # Use SQLAlchemyJobStore if available
            from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
            self.scheduler.add_jobstore(SQLAlchemyJobStore(url='sqlite:///scheduler_jobs.db'))
            print("Using SQLAlchemy job store for persistence")
        except ImportError:
            # Fall back to memory job store
            print("SQLAlchemy not available, using memory job store (jobs will be lost on restart)")
            pass

        # Start the scheduler
        self.scheduler.start()
        print("Commit scheduler initialized and started")

    def setup_daily_commits(self, username: str, token: str, repo_name: str) -> None:
        """
        Set up daily scheduling of commits

        Args:
            username: GitHub username
            token: GitHub token
            repo_name: Repository name
        """
        print(f"Setting up daily commits for {username}/{repo_name}")

        # Schedule today's commits immediately
        schedule_todays_commits_job(username, token, repo_name)

        # Set up recurring daily job to schedule commits at the start of each day
        scheduler_job_id = f"{username}_daily_scheduler"

        # Remove any existing scheduler for this user
        if scheduler_job_id in user_jobs.get(username, []):
            try:
                self.scheduler.remove_job(scheduler_job_id)
                print(f"Removed existing daily scheduler for {username}")
            except Exception as e:
                print(f"Error removing existing scheduler: {str(e)}")

        # Add the new midnight scheduler
        self.scheduler.add_job(
            func=schedule_todays_commits_job,
            trigger=CronTrigger(hour=0, minute=0),
            id=scheduler_job_id,
            args=[username, token, repo_name],
            replace_existing=True
        )

        print(f"Added daily scheduler for {username} at midnight")

        if username not in user_jobs:
            user_jobs[username] = []
        user_jobs[username].append(scheduler_job_id)

    def setup_midnight_scheduler(self, username: str, token: str, repo_name: str) -> None:
        """
        Set up only the midnight scheduler job

        Args:
            username: GitHub username
            token: GitHub token
            repo_name: Repository name
        """
        print(f"Setting up midnight scheduler for {username}/{repo_name}")

        # Add job to run at midnight each day
        scheduler_job_id = f"{username}_daily_scheduler"

        try:
            # Add the midnight scheduler with replace_existing=True
            self.scheduler.add_job(
                func=schedule_todays_commits_job,
                trigger=CronTrigger(hour=0, minute=0),
                id=scheduler_job_id,
                args=[username, token, repo_name],
                replace_existing=True
            )

            print(f"Added midnight scheduler for {username}")

            # Update user_jobs tracking
            if username not in user_jobs:
                user_jobs[username] = []
            if scheduler_job_id not in user_jobs[username]:
                user_jobs[username].append(scheduler_job_id)

        except Exception as e:
            print(f"Error setting up midnight scheduler for {username}: {str(e)}")

    def get_scheduled_commits_count(self, username: str) -> int:
        """
        Get the number of scheduled commits for a user

        Args:
            username: GitHub username

        Returns:
            Number of scheduled commits
        """
        return len([job_id for job_id in user_jobs.get(username, [])
                   if not job_id.endswith("daily_scheduler")])

    def update_next_commit_info(self, username: str) -> None:
        """
        Update the next commit information after a commit has been processed

        Args:
            username: GitHub username
        """
        print(f"Updating next commit information for {username}")
        # This method is called after a commit is processed
        # It doesn't need to return anything as it just updates the internal state
        # The frontend will fetch the updated information on its next API call

        # The next_commit information is already updated by get_next_commit_time
        # We just need to ensure it's called after a commit is processed
        self.get_next_commit_time(username)

    def get_next_commit_time(self, username: str) -> dict:
        """
        Get the next scheduled commit time for a user

        Args:
            username: GitHub username

        Returns:
            Dictionary with next commit information:
            {
                'has_scheduled_commits': bool,
                'next_commit_time': datetime or None,
                'seconds_until_next': int or None,
                'formatted_time': str or None,
                'formatted_countdown': str or None
            }
        """
        print(f"Getting next commit time for {username}")

        result = {
            'has_scheduled_commits': False,
            'next_commit_time': None,
            'seconds_until_next': None,
            'formatted_time': None,
            'formatted_countdown': None
        }

        # Get all job IDs for this user that are not daily schedulers
        commit_job_ids = [job_id for job_id in user_jobs.get(username, [])
                         if not job_id.endswith("daily_scheduler")]

        print(f"Found {len(commit_job_ids)} commit job IDs for {username}: {commit_job_ids}")

        if not commit_job_ids:
            print(f"No commit jobs found for {username}")
            return result

        # Get all jobs from the scheduler
        try:
            all_jobs = self.scheduler.get_jobs()
            print(f"Total jobs in scheduler: {len(all_jobs)}")

            # Filter to only this user's commit jobs
            user_jobs_list = [job for job in all_jobs if job.id in commit_job_ids]
            print(f"Found {len(user_jobs_list)} jobs for {username}")

            if not user_jobs_list:
                print(f"No matching jobs found in scheduler for {username}")
                return result

            # Sort jobs by next run time
            user_jobs_list.sort(key=lambda job: job.next_run_time if job.next_run_time else datetime.datetime.max.replace(tzinfo=datetime.timezone.utc))

            # Get the next job
            next_job = user_jobs_list[0]
            next_time = next_job.next_run_time

            print(f"Next job for {username}: {next_job.id}, run time: {next_time}")

            if next_time:
                # Calculate seconds until next commit
                now = datetime.datetime.now(next_time.tzinfo)
                seconds_until_next = max(0, int((next_time - now).total_seconds()))

                # Format the time
                formatted_time = next_time.strftime('%Y-%m-%d %H:%M:%S')

                # Format the countdown
                hours, remainder = divmod(seconds_until_next, 3600)
                minutes, seconds = divmod(remainder, 60)
                formatted_countdown = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                result = {
                    'has_scheduled_commits': True,
                    'next_commit_time': next_time,
                    'seconds_until_next': seconds_until_next,
                    'formatted_time': formatted_time,
                    'formatted_countdown': formatted_countdown
                }

                print(f"Next commit for {username} in {formatted_countdown} ({seconds_until_next} seconds)")
            else:
                print(f"Next job for {username} has no run time")

        except Exception as e:
            print(f"Error getting next commit time for {username}: {str(e)}")
            import traceback
            traceback.print_exc()

        return result

    def restore_schedulers(self) -> None:
        """Restore schedulers for all users with repositories"""
        print("Restoring schedulers for all users with repositories")

        # Get all users with repositories
        users_with_repos = db.get_users_with_repositories()

        # First, clear any existing jobs that might conflict
        global user_jobs
        try:
            # Get all job IDs from the scheduler
            job_ids = [job.id for job in self.scheduler.get_jobs()]
            print(f"Found {len(job_ids)} existing jobs in the scheduler")

            # Clear user_jobs dictionary to avoid stale references
            user_jobs = {}
        except Exception as e:
            print(f"Error getting existing jobs: {str(e)}")
            # Continue with empty user_jobs
            user_jobs = {}

        for user in users_with_repos:
            try:
                print(f"Restoring scheduler for {user['username']}/{user['repo_name']}")

                # First set up the midnight scheduler
                self.setup_midnight_scheduler(user['username'], user['token'], user['repo_name'])

                # Check if we need to schedule today's commits
                now = datetime.datetime.now()
                midnight = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)

                # If it's been less than 1 hour since midnight, don't schedule again
                # as the midnight job might have already run
                if (now - midnight).total_seconds() > 3600:
                    # Check if there are already commits scheduled for today
                    if self.get_scheduled_commits_count(user['username']) == 0:
                        print(f"No commits scheduled for today for {user['username']}, scheduling now")
                        try:
                            schedule_todays_commits_job(user['username'], user['token'], user['repo_name'])
                        except Exception as e:
                            print(f"Error scheduling today's commits for {user['username']}: {str(e)}")
            except Exception as e:
                print(f"Error restoring scheduler for {user.get('username', 'unknown')}: {str(e)}")
                continue

        print(f"Restored schedulers for {len(users_with_repos)} users")

# Create a global instance of the scheduler
commit_scheduler = CommitScheduler()

def clear_job_store():
    """
    Utility function to clear the job store
    This can be called manually if needed to reset the scheduler
    """
    global user_jobs
    try:
        print("Clearing job store...")
        # Get all jobs
        jobs = commit_scheduler.scheduler.get_jobs()
        print(f"Found {len(jobs)} jobs")

        # Remove each job
        for job in jobs:
            commit_scheduler.scheduler.remove_job(job.id)
            print(f"Removed job {job.id}")

        # Reset user_jobs
        user_jobs = {}

        print("Job store cleared successfully")
        return True
    except Exception as e:
        print(f"Error clearing job store: {str(e)}")
        return False