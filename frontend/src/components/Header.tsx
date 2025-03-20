import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User } from '../types/index';
import { logout } from '../services/api';
import ThemeToggle from './ThemeToggle';

interface HeaderProps {
  user: User | null;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
}

const Header: React.FC<HeaderProps> = ({ user, setUser }) => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex-shrink-0 flex items-center">
            <Link to="/" className="text-xl font-bold text-blue-600 dark:text-blue-400 clickable">
              GitHub Automation
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            <ThemeToggle />

            {user?.authenticated ? (
              <>
                <span className="text-gray-700 dark:text-gray-300">
                  Hello, {user.username}
                </span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-white rounded transition-colors duration-200 clickable"
                >
                  Log out
                </button>
              </>
            ) : (
              <div className="flex space-x-2">
                <Link
                  to="/login"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors duration-200 clickable"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-white rounded transition-colors duration-200 clickable"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;