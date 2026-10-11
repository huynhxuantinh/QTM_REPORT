import React, { useEffect, useState } from 'react';
import { authService } from '@/features/auth/services/authService';
import { LoginRequest } from '@/types/auth';
import { AuthContext } from '@/context/auth-context';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('nhc_token'));
  const [username, setUsername] = useState<string | null>(() => localStorage.getItem('nhc_user'));

  useEffect(() => {
    const handleUnauthorized = () => {
      setToken(null);
      setUsername(null);
      localStorage.removeItem('nhc_token');
      localStorage.removeItem('nhc_user');
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, []);

  const login = async (credentials: LoginRequest) => {
    const data = await authService.login(credentials);
    setToken(data.access_token);
    setUsername(credentials.username);
    localStorage.setItem('nhc_token', data.access_token);
    localStorage.setItem('nhc_user', credentials.username);
  };

  const logout = () => {
    setToken(null);
    setUsername(null);
    localStorage.removeItem('nhc_token');
    localStorage.removeItem('nhc_user');
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!token,
        username,
        token,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
