import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
      {/* Animated code background */}
      <div className="absolute inset-0 overflow-hidden opacity-10 dark:opacity-20 pointer-events-none">
        <div className="code-background text-xs sm:text-sm md:text-base text-gray-700 dark:text-gray-300 font-mono overflow-hidden">
          {Array(30).fill(0).map((_, i) => (
            <div key={i} className="code-line" style={{ animationDelay: `${i * 0.1}s` }}>
              {`// Keep your GitHub profile active`}
              {`function autoCommit() {`}
              {`  const today = new Date();`}
              {`  const commit = createCommit(today);`}
              {`  pushToGitHub(commit);`}
              {`  return "Profile updated successfully";`}
              {`}`}
            </div>
          ))}
        </div>
      </div>

      <div className="container mx-auto px-4 py-16 relative z-10">
        <div className="flex flex-col items-center justify-center text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-800 dark:text-white mb-6">
            Keep Your GitHub Profile Active
          </h1>

          <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 max-w-3xl mb-10">
            Maintain a consistent GitHub activity graph even during your busiest weeks with automated daily commits.
          </p>

          <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-xl max-w-4xl mb-12">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-800 dark:text-white mb-6">
              How Our System Helps You
            </h2>

            <div className="grid md:grid-cols-3 gap-6 text-left">
              <div className="bg-blue-50 dark:bg-blue-900/30 p-5 rounded-lg">
                <h3 className="text-xl font-semibold text-blue-700 dark:text-blue-300 mb-2">Consistent Activity</h3>
                <p className="text-gray-700 dark:text-gray-300">Automated daily commits ensure your GitHub activity graph stays green, even when you're busy.</p>
              </div>

              <div className="bg-purple-50 dark:bg-purple-900/30 p-5 rounded-lg">
                <h3 className="text-xl font-semibold text-purple-700 dark:text-purple-300 mb-2">Impress Employers</h3>
                <p className="text-gray-700 dark:text-gray-300">Show potential employers a consistently active GitHub profile that highlights your dedication.</p>
              </div>

              <div className="bg-green-50 dark:bg-green-900/30 p-5 rounded-lg">
                <h3 className="text-xl font-semibold text-green-700 dark:text-green-300 mb-2">Set & Forget</h3>
                <p className="text-gray-700 dark:text-gray-300">Configure once and let our system handle the rest. No daily maintenance required.</p>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              to="/login"
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200 clickable"
            >
              Login
            </Link>
            <Link
              to="/signup"
              className="px-8 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-white font-medium rounded-lg transition-colors duration-200 clickable"
            >
              Sign Up
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;