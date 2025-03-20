import axios from 'axios';
import { User, Repository, AutomationStatus, CreateRepositoryRequest } from '../types/index';

// Use environment variable for API URL with fallback
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

console.log('API Base URL:', API_BASE_URL);
console.log('Vite Environment Variables:', import.meta.env);
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create axios instance
// const api = axios.create({
//   baseURL: '/api',
//   withCredentials: true,
// });

// User API calls
export const getUserStatus = async (): Promise<User> => {
  const response = await api.get('/user');
  return response.data;
};

export const logout = async (): Promise<void> => {
  await api.post('/logout');
};

// GitHub API calls
export const createRepository = async (data: CreateRepositoryRequest): Promise<Repository> => {
  const response = await api.post('/create-repository', data);
  return response.data.repo;
};

export const getAutomationStatus = async (): Promise<AutomationStatus> => {
  const response = await api.get('/github/status');
  return response.data;
};

export default api;