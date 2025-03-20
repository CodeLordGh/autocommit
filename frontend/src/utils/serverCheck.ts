/**
 * Utility function to check if the server is available
 * @param baseUrl - The base URL of the server (e.g., https://your-backend.onrender.com)
 * @returns Promise that resolves to the server status
 */
export async function checkServerStatus(baseUrl: string): Promise<{
  available: boolean;
  message: string;
  timestamp?: string;
  responseTime: number;
}> {
  const startTime = new Date().getTime();
  
  try {
    const response = await fetch(`${baseUrl}/`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });
    
    const endTime = new Date().getTime();
    const responseTime = endTime - startTime;
    
    if (!response.ok) {
      return {
        available: false,
        message: `Server returned status: ${response.status}`,
        responseTime
      };
    }
    
    const data = await response.json();
    
    return {
      available: true,
      message: data.message || 'Server is available',
      timestamp: data.timestamp,
      responseTime
    };
  } catch (error) {
    const endTime = new Date().getTime();
    const responseTime = endTime - startTime;
    
    return {
      available: false,
      message: error instanceof Error ? error.message : 'Unknown error occurred',
      responseTime
    };
  }
}

/**
 * Example usage:
 * 
 * import { checkServerStatus } from './utils/serverCheck';
 * 
 * // In a React component
 * useEffect(() => {
 *   const checkServer = async () => {
 *     const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
 *     const status = await checkServerStatus(apiUrl);
 *     
 *     if (status.available) {
 *       console.log('Server is available!', status);
 *     } else {
 *       console.error('Server is not available:', status.message);
 *     }
 *   };
 *   
 *   checkServer();
 * }, []);
 */