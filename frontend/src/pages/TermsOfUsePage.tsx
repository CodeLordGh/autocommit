import React from 'react';
import { Link } from 'react-router-dom';

const TermsOfUsePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          <div className="flex justify-center mb-6">
            <img src="/trace (1).svg" alt="KCommit Logo" className="h-16" />
          </div>
          
          <h1 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">
            Terms of Use
          </h1>
          
          <div className="prose dark:prose-invert max-w-none">
            <h2 className="text-2xl font-semibold mb-4">1. Acceptance of Terms</h2>
            <p className="mb-4">
              By accessing or using KCommit, you agree to be bound by these Terms of Use. If you do not agree to these terms, please do not use our service.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">2. Description of Service</h2>
            <p className="mb-4">
              KCommit provides a service that automates GitHub commits to maintain a consistent activity graph. The service creates a repository on your GitHub account and makes scheduled commits to it.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">3. GitHub Account Integration</h2>
            <p className="mb-4">
              Our service requires access to your GitHub account through OAuth authentication. We only perform actions that you explicitly authorize, such as creating repositories and making commits on your behalf.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">4. User Responsibilities</h2>
            <p className="mb-4">
              You are responsible for maintaining the confidentiality of your account information and for all activities that occur under your account. You agree to notify us immediately of any unauthorized use of your account.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">5. Limitations of Service</h2>
            <p className="mb-4">
              While we strive to provide a reliable service, we cannot guarantee that the service will be uninterrupted or error-free. We reserve the right to modify, suspend, or discontinue the service at any time without notice.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">6. Intellectual Property</h2>
            <p className="mb-4">
              All content, features, and functionality of our service, including but not limited to text, graphics, logos, and code, are owned by KCommit and are protected by copyright, trademark, and other intellectual property laws.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">7. Termination</h2>
            <p className="mb-4">
              We reserve the right to terminate or suspend your account and access to our service at our sole discretion, without notice, for conduct that we believe violates these Terms of Use or is harmful to other users, us, or third parties, or for any other reason.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">8. Changes to Terms</h2>
            <p className="mb-4">
              We reserve the right to modify these Terms of Use at any time. We will provide notice of significant changes by updating the date at the top of these terms and by maintaining a current version of the terms at our website.
            </p>
            
            <h2 className="text-2xl font-semibold mb-4">9. Contact Information</h2>
            <p className="mb-4">
              If you have any questions about these Terms of Use, please contact us at support@kcommit.com.
            </p>
          </div>
          
          <div className="mt-8 text-center">
            <Link to="/privacy" className="text-blue-600 dark:text-blue-400 hover:underline mr-4 clickable">
              Privacy Policy
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

export default TermsOfUsePage;