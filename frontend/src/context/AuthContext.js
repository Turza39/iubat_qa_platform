'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { jwtDecode } from 'jwt-decode';
import { authService } from '@/services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const decoded = jwtDecode(token);
        // Check if token is expired
        const isExpired = decoded.exp * 1000 < Date.now();
        if (isExpired) {
          logout();
        } else {
          loadUserProfile();
        }
      }
    } catch (error) {
      logout();
    } finally {
      setLoading(false);
    }
  };

  const loadUserProfile = async () => {
    try {
      const data = await authService.getProfile();
      setUser(data.profile);
    } catch (error) {
      logout();
    }
  };

  const login = async (credentials) => {
    const data = await authService.login(credentials);
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    await loadUserProfile();
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const refreshUser = async () => {
    await loadUserProfile();
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};