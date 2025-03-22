import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Commit {
  id: number;
  username: string;
  repo_name: string;
  commit_sha: string;
  commit_message: string;
  commit_url: string;
  timestamp: string;
}

interface CommitHistoryProps {
  username: string;
  repoName: string;
}

const CommitHistory: React.FC<CommitHistoryProps> = ({ username, repoName }) => {
  const [commits, setCommits] = useState<Commit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCommits = async () => {
      try {
        // First try our database API
        const response = await axios.get('/api/commits', { 
          withCredentials: true,
          headers: {
            'Accept': 'application/json'
          }
        });
        
        // Check if the response is valid JSON data
        if (response.data && typeof response.data === 'object' && Array.isArray(response.data)) {
          setCommits(response.data);
        } else {
          // If we got an invalid response, throw an error to trigger the fallback
          throw new Error('Invalid response format from server');
        }
      } catch (err) {
        // Fallback to GitHub API for public repos
        try {
          if (username && repoName) {
            const githubResponse = await axios.get(
              `https://api.github.com/repos/${username}/${repoName}/commits`,
              { params: { per_page: 10 } }
            );
            
            // Transform GitHub API response to match our format
            const transformedCommits = githubResponse.data.map((item: any) => ({
              id: item.sha,
              username,
              repo_name: repoName,
              commit_sha: item.sha,
              commit_message: item.commit.message,
              commit_url: item.html_url,
              timestamp: item.commit.author.date
            }));
            
            setCommits(transformedCommits);
          } else {
            setError('Repository information is missing');
          }
        } catch (githubErr) {
          setError('Failed to load commit history');
        }
      } finally {
        setLoading(false);
      }
    };

    if (username && repoName) {
      fetchCommits();
    } else {
      setLoading(false);
      setError('Repository information is missing');
    }
  }, [username, repoName]);

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Recent Commits</h2>
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Recent Commits</h2>
        <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Recent Commits</h2>
       {!Array.isArray(commits) && <p>{commits}</p>}
      {Array.isArray(commits) && commits.length === 0 ? (
        <p className="text-gray-500 dark:text-gray-400">No commits found in this repository yet.</p>
      ) : (
        <div className="max-h-80 overflow-y-auto pr-2 custom-scrollbar">
          <div className="space-y-4">
            
            {/* Map over the commits and render them */}
            {Array.isArray(commits) && commits.map((commit) => (
              <div key={commit.commit_sha} className="border-b dark:border-gray-700 pb-4 last:border-b-0">
                <div className="flex justify-between">
                  <a
                    href={commit.commit_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-blue-400 hover:underline font-medium clickable"
                  >
                    {commit.commit_message}
                  </a>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {new Date(commit.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {commit.commit_sha.substring(0, 7)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CommitHistory;