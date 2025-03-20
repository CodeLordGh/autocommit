import React, { useState } from 'react';
import { Repository } from '../types';
import { createRepository } from '../services/api';

interface RepositoryFormProps {
  onRepositoryCreated: (repository: Repository) => void;
}

const RepositoryForm: React.FC<RepositoryFormProps> = ({ onRepositoryCreated }) => {
  const [repoName, setRepoName] = useState('');
  const [description, setDescription] = useState('Repository for automated commits');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [suggestedNames, setSuggestedNames] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuggestedNames([]);

    try {
      const response = await createRepository({ repoName, description });
      onRepositoryCreated(response);
    } catch (err: any) {
      // Extract error information
      let errorMessage = 'Failed to create repository';

      if (err.response) {
        const { data, status } = err.response;

        // Handle name conflict (409 Conflict)
        if (status === 409 && data.name_conflict) {
          errorMessage = data.error || `Repository '${repoName}' already exists`;

          // Set suggested names if available
          if (data.suggested_names && Array.isArray(data.suggested_names)) {
            setSuggestedNames(data.suggested_names);
          }
        } else if (data && data.error) {
          // Handle other errors
          errorMessage = data.error;
        }
      } else if (err.request) {
        // Request was made but no response received
        errorMessage = 'No response received from server. Please check your connection.';
      } else {
        // Something else caused the error
        errorMessage = err.message || errorMessage;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Handle clicking on a suggested name
  const handleSuggestedNameClick = (name: string) => {
    setRepoName(name);
    setSuggestedNames([]);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 px-4 py-3 rounded">
          <div className="font-bold mb-1">Error:</div>
          <div>{error}</div>

          {/* Display suggested names if available */}
          {suggestedNames.length > 0 && (
            <div className="mt-3">
              <div className="font-medium">Suggested alternative names:</div>
              <div className="flex flex-wrap gap-2 mt-2">
                {suggestedNames.map((name, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleSuggestedNameClick(name)}
                    className="px-3 py-1 bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200 rounded hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors clickable"
                  >
                    {name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div>
        <label htmlFor="repoName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Repository Name
        </label>
        <input
          type="text"
          id="repoName"
          value={repoName}
          onChange={(e) => setRepoName(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          placeholder="e.g. github-automation"
          required
        />
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Repository names can only contain alphanumeric characters, hyphens, and underscores.
        </p>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Description
        </label>
        <input
          type="text"
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          placeholder="Repository description"
        />
      </div>

      <button
        type="submit"
        className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded transition-colors duration-200 clickable"
        disabled={loading}
      >
        {loading ? (
          <span className="flex items-center justify-center">
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Creating...
          </span>
        ) : 'Create Repository'}
      </button>
    </form>
  );
};

export default RepositoryForm;