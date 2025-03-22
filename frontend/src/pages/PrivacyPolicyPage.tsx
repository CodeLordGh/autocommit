import React from 'react';
import { Link } from 'react-router-dom';

const PrivacyPolicyPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          <div className="flex justify-center mb-6">
            <img src="/trace (1).svg" alt="KCommit Logo" className="h-16" />
          </div>
          
          <h1 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">
            Privacy Policy
          </h1>
          
          <div className="prose dark:prose-invert max-w-none">
            <h2 className="text-2xl font-semibold mb-4">1. Information We Collect</h2>
            <p className="mb-4">
              When you use KCommit, we collect the following information:
            </p>
            <ul className="list-disc pl-6 mb-4">
              <li>Your GitHub username and access token (securely stored)</li>
              <li>Repository names that you create through our service</li>
              <li>Commit history for repositories managed by our service</li>
              <li>Webhook secrets for repository integrations</li>
            </ul>
            
            <h2 className="text-2xl font-semibold mb-4">2. How We Use Your Information</h2>
            <p className="mb-4">
              We use the collected information for the following purposes:
            </p>
            <ul className="list-disc pl-6 mb-4">
              <li>To authenticate with GitHub on your behalf</li>
              <li>To create and manage repositories for automated commits</li>
              <li>To schedule and make commits to your repositories</li>
              <li>To display your commit history within our application</li>
            </ul>
            
            <h2 className="text-2xl font-semibold mb-4">3. Data Storage and Security</h2>
            <p className="mb-4">
              Your data is stored in a secure SQLite database. We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. Your GitHub access token is stored securely and is only used for the specific actions you authorize.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">4. Third-Party Services</h2>
            <p className="mb-4">
              We use GitHub's API to provide our service. Your interaction with GitHub through our service is also subject to GitHub's Privacy Policy. We encourage you to review GitHub's privacy practices.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">5. Data Retention</h2>
            <p className="mb-4">
              We retain your data for as long as your account is active or as needed to provide you with our services. If you wish to delete your data, you can request account deletion, and we will remove your personal information from our database.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">6. Your Rights</h2>
            <p className="mb-4">
              You have the right to access, correct, or delete your personal information. You can also revoke our access to your GitHub account at any time through GitHub's settings.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">7. Cookies and Tracking</h2>
            <p className="mb-4">
              We use session cookies to maintain your login state. These cookies are essential for the functioning of our service and do not track your activities outside of our application.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">8. Changes to This Privacy Policy</h2>
            <p className="mb-4">
              We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the effective date.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">9. Contact Us</h2>
            <p className="mb-4">
              If you have any questions about this Privacy Policy, please contact us at privacy@kcommit.com.
            </p>
          </div>
          
          <div className="mt-8 text-center">
            <Link to="/terms" className="text-blue-600 dark:text-blue-400 hover:underline mr-4 clickable">
              Terms of Use
            </Link>
            <Link to="/" className="text-blue-600 dark:text-blue-400 hover:underline clickable">
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicyPage;