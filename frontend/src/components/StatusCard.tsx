import React, { useState, useEffect } from 'react';
import { AutomationStatus, Repository } from '../types';

interface StatusCardProps {
  status: AutomationStatus | null;
  repository: Repository;
}

const StatusCard: React.FC<StatusCardProps> = ({ status, repository }) => {
  const [countdown, setCountdown] = useState<string | null>(null);

  // Debug logging
  useEffect(() => {
    console.log("StatusCard rendered with status:", status);
    if (status && status.next_commit) {
      console.log("Next commit info:", status.next_commit);
    }
  }, [status]);

  // Update countdown every second
  useEffect(() => {
    // Only log in development environment
    if (import.meta.env?.MODE === 'development' || import.meta.env?.DEV) {
      console.log("Countdown effect running with status:", status);
    }

    if (!status) {
      return;
    }

    if (!status.next_commit) {
      return;
    }

    if (!status.next_commit.has_scheduled_commits) {
      // This is normal when no commits are scheduled yet
      return;
    }

    if (!status.next_commit.seconds_until_next) {
      return;
    }

    // Initialize countdown
    let secondsRemaining = status.next_commit.seconds_until_next;
    console.log(`Initializing countdown with ${secondsRemaining} seconds remaining`);
    setCountdown(formatCountdown(secondsRemaining));

    // Set up interval to update countdown
    const intervalId = setInterval(() => {
      secondsRemaining -= 1;

      if (secondsRemaining <= 0) {
        console.log("Countdown reached zero");
        clearInterval(intervalId);
        setCountdown("Commit in progress...");

        // Instead of refreshing the whole page, poll the API for updated status
        const checkForUpdates = async () => {
          try {
            // Import the API function dynamically to avoid circular dependencies
            const { getAutomationStatus } = await import('../services/api');
            const updatedStatus = await getAutomationStatus();

            // If we get a response, the commit is likely complete
            if (updatedStatus && updatedStatus.next_commit) {
              // If there are more scheduled commits, update the countdown
              if (updatedStatus.next_commit.has_scheduled_commits &&
                  updatedStatus.next_commit.seconds_until_next) {
                // Force a re-render by updating the status prop
                window.location.reload();
              } else {
                setCountdown("No more commits scheduled for today");
              }
            }
          } catch (error) {
            console.error("Error checking for status updates:", error);
            // If we can't get an update, fall back to page refresh
            window.location.reload();
          }
        };

        // Check for updates after 5 seconds, then every 5 seconds until we get an update
        const updateCheckerId = setInterval(checkForUpdates, 5000);
        setTimeout(() => {
          checkForUpdates();
          // If we haven't gotten an update after 30 seconds, force a refresh
          setTimeout(() => {
            clearInterval(updateCheckerId);
            window.location.reload();
          }, 30000);
        }, 5000);
      } else {
        setCountdown(formatCountdown(secondsRemaining));
      }
    }, 1000);

    // Clean up interval
    return () => {
      console.log("Cleaning up countdown interval");
      clearInterval(intervalId);
    };
  }, [status]);

  // Format seconds into HH:MM:SS
  const formatCountdown = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (!status) return null;

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Repository Status</h2>

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-medium mb-2 text-gray-800 dark:text-gray-200">Repository Details</h3>
          <p className="mb-1 text-gray-700 dark:text-gray-300">
            <span className="font-medium">Name:</span> {repository.name}
          </p>
          <p className="mb-3">
            <a
              href={repository.html_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 dark:text-blue-400 hover:underline clickable"
            >
              View on GitHub
            </a>
          </p>
        </div>

        <div>
          <h3 className="text-lg font-medium mb-2 text-gray-800 dark:text-gray-200">Commit Status</h3>
          <p className="mb-1 text-gray-700 dark:text-gray-300">
            <span className="font-medium">Today's Scheduled Commits:</span> {status.scheduled_commits}
          </p>
          <p className="mb-1 text-gray-700 dark:text-gray-300">
            <span className="font-medium">Total Commits:</span> {status.total_commits}
          </p>

          {status.next_commit.has_scheduled_commits && (
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/30 rounded-md">
              <h4 className="font-medium text-blue-700 dark:text-blue-300">Next Commit</h4>
              <div className="flex items-center mt-2">
                <div className="w-8 h-8 bg-blue-100 dark:bg-blue-800 rounded-full flex items-center justify-center mr-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-600 dark:text-blue-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Scheduled for: <span className="font-medium">{status.next_commit.formatted_time}</span>
                  </p>
                  <p className="text-lg font-bold text-blue-700 dark:text-blue-300 mt-1">
                    {countdown || status.next_commit.formatted_countdown}
                  </p>
                </div>
              </div>
            </div>
          )}

          {!status.next_commit.has_scheduled_commits && (
            <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
              <p className="text-sm text-gray-600 dark:text-gray-300">
                <span className="font-medium">Status:</span> Waiting for next commit cycle
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                New commits are scheduled each day at 12:00 AM. {status.scheduled_commits > 0 ?
                  `${status.scheduled_commits} commits are scheduled for today.` :
                  'Check back tomorrow for new automated commits.'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatusCard;