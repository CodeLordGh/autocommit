import { useState, useEffect } from 'react';
import { checkServerStatus } from '../utils/serverCheck';
import './ServerStatus.css';

interface ServerStatusProps {
  apiUrl?: string;
  onStatusChange?: (isAvailable: boolean) => void;
}

export default function ServerStatus({ 
  apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  onStatusChange 
}: ServerStatusProps) {
  const [status, setStatus] = useState<{
    checking: boolean;
    available: boolean;
    message: string;
    timestamp?: string;
    responseTime?: number;
  }>({
    checking: true,
    available: false,
    message: 'Checking server status...'
  });

  useEffect(() => {
    let isMounted = true;
    
    const checkServer = async () => {
      try {
        const result = await checkServerStatus(apiUrl);
        
        if (isMounted) {
          setStatus({
            checking: false,
            available: result.available,
            message: result.message,
            timestamp: result.timestamp,
            responseTime: result.responseTime
          });
          
          if (onStatusChange) {
            onStatusChange(result.available);
          }
        }
      } catch (error) {
        if (isMounted) {
          setStatus({
            checking: false,
            available: false,
            message: error instanceof Error ? error.message : 'Failed to check server status'
          });
          
          if (onStatusChange) {
            onStatusChange(false);
          }
        }
      }
    };
    
    checkServer();
    
    // Set up periodic checking
    const intervalId = setInterval(checkServer, 30000); // Check every 30 seconds
    
    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [apiUrl, onStatusChange]);

  return (
    <div className="server-status">
      <div className={`status-indicator ${status.checking ? 'checking' : (status.available ? 'available' : 'unavailable')}`}>
        {status.checking ? (
          <span>Checking server...</span>
        ) : status.available ? (
          <span>Server is available</span>
        ) : (
          <span>Server is unavailable</span>
        )}
      </div>

      {!status.checking && (
        <div className="status-details">
          <p>{status.message}</p>
          {status.timestamp && <p>Last updated: {new Date(status.timestamp).toLocaleString()}</p>}
          {status.responseTime !== undefined && <p>Response time: {status.responseTime}ms</p>}
        </div>
      )}
    </div>
  );
}