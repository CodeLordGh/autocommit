import React, { useState, useEffect } from 'react';
import { User, AutomationStatus, Repository } from '../types';
import { getAutomationStatus } from '../services/api';
import RepositoryForm from '../components/RepositoryForm';
import StatusCard from '../components/StatusCard';
import CommitHistory from '../components/CommitHistory';

interface DashboardPageProps {
  user: User;
}

const DashboardPage: React.FC<DashboardPageProps> = ({ user }) => {
  const [status, setStatus] = useState<AutomationStatus | null>(null);
  const [repository, setRepository] = useState<Repository | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Reset repository state when user changes
    setRepository(null);

    // Initialize repository state from user data if available
    if (user.authenticated && user.hasRepository && user.repositoryName) {
      setRepository({
        name: user.repositoryName,
        html_url: `https://github.com/${user.username}/${user.repositoryName}`,
        description: 'Repository for automated commits'
      });
    }

    const fetchStatus = async () => {
      try {
        const statusData = await getAutomationStatus();

        // Ensure next_commit is present with default values if missing
        const normalizedStatusData = {
          ...statusData,
          // Always provide a next_commit object, either from the API or with default values
          next_commit: statusData.next_commit || {
            has_scheduled_commits: false,
            formatted_time: null,
            formatted_countdown: null,
            seconds_until_next: null
          }
        };

        setStatus(normalizedStatusData);

        // Set repository if the user has one on our platform and we don't already have it set from user data
        if (normalizedStatusData.hasRepository && normalizedStatusData.repo_name && !repository) {
          setRepository({
            name: normalizedStatusData.repo_name,
            html_url: `https://github.com/${user.username}/${normalizedStatusData.repo_name}`,
            description: 'Repository for automated commits'
          });
        }
      } catch (error) {
        console.error('Failed to fetch status:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user.authenticated) {
      fetchStatus();
    } else {
      setLoading(false);
    }
  }, [user]);

  const handleCreateRepository = async (repo: Repository) => {
    setRepository(repo);
    // Refresh status after repository creation
    try {
      const statusData = await getAutomationStatus();

      // Apply the same normalization as in fetchStatus
      const normalizedStatusData = {
        ...statusData,
        next_commit: statusData.next_commit || {
          has_scheduled_commits: false,
          formatted_time: null,
          formatted_countdown: null,
          seconds_until_next: null
        }
      };

      setStatus(normalizedStatusData);
    } catch (error) {
      console.error('Failed to refresh status after repository creation');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold mb-8 text-gray-900 dark:text-white">Dashboard</h1>

      {repository ? (
        <div className="space-y-8">
          <StatusCard status={status} repository={repository} />
          <CommitHistory username={user.username || ''} repoName={repository.name} />
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Set Up Automation</h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Create a new GitHub repository to start automating commits. The system will make 1-10 random commits each day to keep your GitHub profile active.
          </p>
          <RepositoryForm onRepositoryCreated={handleCreateRepository} />
        </div>
      )}
    </div>
  );
};

export default DashboardPage;