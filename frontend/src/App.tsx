import { useEffect, useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { User } from './types';
import { getUserStatus } from './services/api';
import { ThemeProvider } from './context/ThemeContext';

// Pages
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import LandingPage from './pages/LandingPage';
import TermsOfUsePage from './pages/TermsOfUsePage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import Header from './components/Header';
import CustomCursor from './components/CustomCursor';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        setLoading(true);
        console.log('Checking authentication status...');
        const userData = await getUserStatus();
        console.log('Authentication status:', userData);
        setUser(userData);
      } catch (error) {
        console.error('Authentication check failed:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    // Add a small delay when checking after a route change to ensure
    // the server has time to process the session
    const timer = setTimeout(() => {
      checkAuthStatus();
    }, 500);

    return () => clearTimeout(timer);
  }, [location.pathname]); // Re-check auth status when route changes (e.g., after login redirect)

  if (loading) {
    return (
      <ThemeProvider>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-200">
          <CustomCursor loading={loading} />
          <div className="flex items-center justify-center min-h-screen">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        </div>
      </ThemeProvider>
    );
  }

  // Define paths where header should be hidden
  const hideHeaderPaths = ["/login", "/signup", "/terms", "/privacy"];
  const shouldShowHeader = !hideHeaderPaths.includes(location.pathname);

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-200">
        <CustomCursor loading={loading} />
        {shouldShowHeader && <Header user={user} setUser={setUser} />}
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={user?.authenticated ? <Navigate to="/dashboard" /> : <LoginPage />} />
          <Route path="/signup" element={user?.authenticated ? <Navigate to="/dashboard" /> : <LoginPage />} />
          <Route
            path="/dashboard"
            element={user?.authenticated ? <DashboardPage user={user} /> : <Navigate to="/login" />}
          />
          <Route path="/terms" element={<TermsOfUsePage />} />
          <Route path="/privacy" element={<PrivacyPolicyPage />} />
        </Routes>
      </div>
    </ThemeProvider>
  );
}

export default App;