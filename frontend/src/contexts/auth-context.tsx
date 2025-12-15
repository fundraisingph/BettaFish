"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { api } from '@/lib/api/client';

// User type definition
export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  created_at: string;
  updated_at: string;
}

// Auth context type
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  register: (email: string, password: string, name: string) => Promise<{ success: boolean; error?: string }>;
  refreshToken: () => Promise<boolean>;
}

// Create auth context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isClient, setIsClient] = useState(false);

  // Set client flag
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Check if user is authenticated on mount
  useEffect(() => {
    // Only run on client side
    if (!isClient) return;
    
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (token) {
          // Verify token with backend
          const response = await api.get<User>('/api/auth/me');
          if (response.success && response.data) {
            setUser(response.data);
          } else {
            // Token is invalid, clear it
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        // Only access localStorage on client side
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [isClient]);

  // Login function
  const login = async (email: string, password: string) => {
    try {
      const response = await api.post<{
        access_token: string;
        refresh_token: string;
        user: User;
      }>('/api/auth/login', { email, password });

      if (response.success && response.data) {
        const { access_token, refresh_token, user } = response.data;
        
        // Store tokens
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
        }
        
        // Set user
        setUser(user);
        
        return { success: true };
      } else {
        return { success: false, error: response.error || 'Login failed' };
      }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  // Logout function
  const logout = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
    setUser(null);
  };

  // Register function
  const register = async (email: string, password: string, name: string) => {
    try {
      const response = await api.post<{
        access_token: string;
        refresh_token: string;
        user: User;
      }>('/api/auth/register', { email, password, name });

      if (response.success && response.data) {
        const { access_token, refresh_token, user } = response.data;
        
        // Store tokens
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
        }
        
        // Set user
        setUser(user);
        
        return { success: true };
      } else {
        return { success: false, error: response.error || 'Registration failed' };
      }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Registration failed' 
      };
    }
  };

  // Refresh token function
  const refreshToken = async () => {
    try {
      if (typeof window === 'undefined') return false;
      const refresh_token = localStorage.getItem('refresh_token');
      if (!refresh_token) return false;

      const response = await api.post<{ access_token: string }>('/api/auth/refresh', {
        refresh_token,
      });

      if (response.success && response.data) {
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', response.data.access_token);
        }
        return true;
      }
      return false;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    register,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}