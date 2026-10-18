import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User } from '../types';
import { api } from '../lib/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (data: { email: string; name: string; role: 'brand' | 'creator'; company?: string; password?: string }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const token = localStorage.getItem('codexero_token') || localStorage.getItem('maccall_token');
    const saved = localStorage.getItem('codexero_user') || localStorage.getItem('maccall_user');
    if (token && saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return null;
      }
    }
    return null;
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('codexero_token') || localStorage.getItem('maccall_token');
      if (token) {
        try {
          const me = await api.auth.getMe();
          setUser(me);
        } catch {
          // Token invalid or backend rejected, clear session
          localStorage.removeItem('codexero_token');
          localStorage.removeItem('codexero_user');
          localStorage.removeItem('maccall_token');
          localStorage.removeItem('maccall_user');
          setUser(null);
        }
      }
    };
    checkAuth();
  }, []);

  const login = async (email: string, pass: string) => {
    setIsLoading(true);
    try {
      const res = await api.auth.login(email, pass);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: { email: string; name: string; role: 'brand' | 'creator'; company?: string; password?: string }) => {
    setIsLoading(true);
    try {
      const res = await api.auth.register(data);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('codexero_token');
    localStorage.removeItem('codexero_user');
    localStorage.removeItem('maccall_token');
    localStorage.removeItem('maccall_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
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
