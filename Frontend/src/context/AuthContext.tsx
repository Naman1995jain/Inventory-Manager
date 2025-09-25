'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import { User, Token, UserLogin, UserCreate } from '@/types';
import { authService } from '@/lib/services';
import LoginSecurityManager from '@/lib/loginSecurity';
import toast from 'react-hot-toast';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (credentials: UserLogin) => Promise<void>;
  register: (userData: UserCreate) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Clean up expired locks on app start
    LoginSecurityManager.cleanupExpiredLocks();
    
    // Check if user is logged in on app start
    const token = Cookies.get('token');
    const userData = Cookies.get('user');
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        
        // Validate token format (basic check)
        if (token.includes('.') && token.split('.').length === 3) {
          setUser(parsedUser);
        } else {
          // Invalid token format, clear cookies
          Cookies.remove('token');
          Cookies.remove('user');
        }
      } catch (error) {
        // Invalid user data, clear cookies
        Cookies.remove('token');
        Cookies.remove('user');
      }
    }
    
    setIsLoading(false);
  }, []);

  const login = async (credentials: UserLogin) => {
    // Check if account is locked
    const lockStatus = LoginSecurityManager.isLocked(credentials.email);
    if (lockStatus.locked) {
      toast.error(`Account locked. Try again in ${lockStatus.remainingTime} seconds.`);
      throw new Error('Account locked');
    }

    try {
      const tokenResponse: Token = await authService.login(credentials);
      
      // Reset failed attempts on successful login
      LoginSecurityManager.resetAttempts(credentials.email);
      
      // Store token
      Cookies.set('token', tokenResponse.access_token, { expires: 7 }); // 7 days
      
      // Decode JWT to extract user information
      let userData: User;
      try {
        // Basic JWT decoding (payload is the middle part)
        const jwtPayload = JSON.parse(atob(tokenResponse.access_token.split('.')[1]));
        
        // Extract user information from JWT payload
        userData = {
          id: jwtPayload.user_id || 0,
          email: credentials.email,
          created_at: new Date().toISOString(),
        };
      } catch (jwtError) {
        // Fallback if JWT decoding fails
        userData = {
          id: 0,
          email: credentials.email,
          created_at: new Date().toISOString(),
        };
      }
      
      Cookies.set('user', JSON.stringify(userData), { expires: 7 });
      setUser(userData);
      
      toast.success('Login successful!');
    } catch (error: any) {
      // Record failed attempt
      const attemptResult = LoginSecurityManager.recordFailedAttempt(credentials.email);
      
      let message = 'Login failed';
      if (error.response?.status === 401) {
        if (attemptResult.locked) {
          message = `Too many failed attempts. Account locked for 60 seconds.`;
        } else {
          const remainingAttempts = 3 - attemptResult.attempts;
          message = `Invalid email or password. ${remainingAttempts} attempt${remainingAttempts !== 1 ? 's' : ''} remaining.`;
        }
      } else {
        message = error.response?.data?.detail || 'Login failed';
      }
      
      toast.error(message);
      throw error;
    }
  };

  const register = async (userData: UserCreate) => {
    try {
      const newUser = await authService.register(userData);
      toast.success('Registration successful! Please log in.');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed';
      toast.error(message);
      throw error;
    }
  };

  const logout = () => {
    Cookies.remove('token');
    Cookies.remove('user');
    setUser(null);
    toast.success('Logged out successfully');
  };

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};