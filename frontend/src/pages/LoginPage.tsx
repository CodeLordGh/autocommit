import React, { useEffect } from 'react';

const LoginPage: React.FC = () => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
  // const apiBaseUrl = "http://localhost:5000"

  useEffect(() => {
    // Log the API base URL for debugging
    console.log('API Base URL:', apiBaseUrl);
  }, [apiBaseUrl]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] px-4">
      <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-8 max-w-lg w-full text-center">
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">GitHub Automation</h1>
        <p className="text-gray-600 dark:text-gray-300 mb-8">
          Create GitHub repositories and automate daily commits to maintain your activity graph.
        </p>

        <div className="space-y-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Sign in with your GitHub account to get started
          </p>
          <a
            href={`${apiBaseUrl}/github/login`}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 inline-flex items-center justify-center w-full"
          >
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path fillRule="evenodd" d="M10 0C4.477 0 0 4.477 0 10c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V19c0 .27.16.59.67.5C17.14 18.16 20 14.42 20 10A10 10 0 0010 0z" clipRule="evenodd" />
            </svg>
            Sign in with GitHub
          </a>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;