import React, { createContext, useContext, useState, useEffect } from 'react';
import axios, { AxiosError } from 'axios';

interface AuthContextType {
  isAuthenticated: boolean;
  accessToken: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Fallback storage if localStorage is not available
const storage = {
  getItem: (key: string): string | null => {
    try {
      return localStorage.getItem(key);
    } catch (error) {
      console.error('Storage getItem error:', error);
      return null;
    }
  },
  setItem: (key: string, value: string): void => {
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      console.error('Storage setItem error:', error);
    }
  },
  removeItem: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Storage removeItem error:', error);
    }
  },
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const token = storage.getItem('accessToken');
      console.log('Stored token:', token ? 'exists' : 'not found');
      if (token) {
        setAccessToken(token);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Token retrieval error:', error);
      setError('Failed to retrieve authentication state');
    } finally {
      setLoading(false);
    }
  }, []);

  const login = async (username: string, password: string) => {
    try {
      setError(null);
      console.log('Attempting login for username:', username);
      
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      formData.append('grant_type', 'password');
      formData.append('remember_me', 'false');
      
      console.log('Making login request...');
      const response = await axios.post('http://localhost:8000/api/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json',
        },
        withCredentials: true,
        validateStatus: (status) => {
          console.log('Response status:', status);
          return true; // Don't throw for any status
        },
      });

      console.log('Login response:', {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
        data: response.data,
      });

      if (response.status !== 200) {
        throw new Error(`Login failed: ${response.status} ${response.statusText}`);
      }

      const { access_token } = response.data;
      if (!access_token) {
        throw new Error('No access token received');
      }

      storage.setItem('accessToken', access_token);
      setAccessToken(access_token);
      setIsAuthenticated(true);
      console.log('Login successful');
    } catch (error) {
      console.error('Login error details:', {
        error,
        isAxiosError: axios.isAxiosError(error),
        response: axios.isAxiosError(error) ? error.response : undefined,
      });

      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError;
        if (axiosError.response) {
          setError(`Login failed: ${axiosError.response.status} ${axiosError.response.statusText}`);
        } else if (axiosError.request) {
          setError('Login failed: No response received from server');
        } else {
          setError(`Login failed: ${axiosError.message}`);
        }
      } else {
        setError(`Login failed: ${(error as Error).message}`);
      }
      throw error;
    }
  };

  const logout = () => {
    try {
      storage.removeItem('accessToken');
      setAccessToken(null);
      setIsAuthenticated(false);
      setError(null);
      console.log('Logout successful');
    } catch (error) {
      console.error('Logout error:', error);
      setError('Failed to logout');
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, accessToken, login, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
