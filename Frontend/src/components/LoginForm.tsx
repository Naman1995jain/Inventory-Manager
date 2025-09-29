'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { UserLogin } from '@/types';
import LoginSecurityManager from '@/lib/loginSecurity';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Eye, EyeOff, Lock, Mail } from 'lucide-react';

export default function LoginForm() {
  const [formData, setFormData] = useState<UserLogin>({
    email: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [lockoutInfo, setLockoutInfo] = useState<{ locked: boolean; remainingTime?: number }>({ locked: false });
  const { login } = useAuth();
  const router = useRouter();

  // Check lockout status when email changes
  useEffect(() => {
    if (formData.email) {
      const lockStatus = LoginSecurityManager.isLocked(formData.email);
      setLockoutInfo(lockStatus);
    }
  }, [formData.email]);

  // Update lockout countdown
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (lockoutInfo.locked && lockoutInfo.remainingTime && lockoutInfo.remainingTime > 0) {
      interval = setInterval(() => {
        setLockoutInfo(prev => {
          if (!prev.remainingTime || prev.remainingTime <= 1) {
            // Lockout expired
            return { locked: false };
          }
          return {
            ...prev,
            remainingTime: prev.remainingTime - 1
          };
        });
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [lockoutInfo.locked, lockoutInfo.remainingTime]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Check if account is locked
    const lockStatus = LoginSecurityManager.isLocked(formData.email);
    if (lockStatus.locked) {
      return; // Don't submit if locked
    }

    setIsLoading(true);

    try {
      await login(formData);
      router.push('/dashboard');
    } catch (error) {
      // Check lockout status after failed login
      const newLockStatus = LoginSecurityManager.isLocked(formData.email);
      setLockoutInfo(newLockStatus);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Gradient Background */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-indigo-600 via-purple-600 to-blue-700">
        <div className="relative z-10 flex flex-col justify-center px-12 text-white">
          <div className="animate-fade-in">
            <h1 className="text-4xl font-bold mb-6 leading-tight">
              Welcome Back to Your
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-400">
                Inventory Hub
              </span>
            </h1>
            <p className="text-xl text-blue-100 leading-relaxed">
              Manage your products, track stock movements, and streamline your business operations with our comprehensive inventory management system.
            </p>
            <div className="mt-8 space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-blue-100">Real-time inventory tracking</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse delay-100"></div>
                <span className="text-blue-100">Advanced stock management</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-pink-400 rounded-full animate-pulse delay-200"></div>
                <span className="text-blue-100">Comprehensive reporting</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Login Form */}
      <div className="w-full lg:w-1/2 flex flex-col justify-center px-6 sm:px-12 lg:px-16 xl:px-24 bg-gradient-to-br from-gray-50 to-white relative">
        {/* Back Button */}
        <div className="absolute top-8 left-8 z-20">
          <Link
            href="/"
            className="group flex items-center space-x-3 px-4 py-2 text-gray-600 hover:text-white bg-white/80 hover:bg-indigo-600 backdrop-blur-sm rounded-full shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-200 hover:border-indigo-600"
          >
            <ArrowLeft size={18} className="transition-transform duration-300 group-hover:-translate-x-1" />
            <span className="font-medium text-sm">Back to Home</span>
          </Link>
        </div>

        <div className="max-w-md mx-auto w-full animate-slide-up">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl mb-6 shadow-lg">
              <Lock className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Sign in to your account
            </h2>
            <p className="text-gray-600">
              Don't have an account?{' '}
              <Link 
                href="/register" 
                className="font-medium text-indigo-600 hover:text-indigo-500 transition-colors"
              >
                Sign up here
              </Link>
            </p>
          </div>

          {/* Lockout Warning */}
          {lockoutInfo.locked && (
            <div className="mb-6 rounded-xl bg-red-50 p-4 border border-red-100 animate-shake">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Lock className="h-5 w-5 text-red-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    Account Temporarily Locked
                  </h3>
                  <div className="mt-1 text-sm text-red-700">
                    <p>
                      Too many failed attempts. Wait{' '}
                      <span className="font-bold text-red-800">{lockoutInfo.remainingTime}s</span> before trying again.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Demo instructions */}
          <div className="mb-6 rounded-xl bg-blue-50 p-4 border border-blue-100">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-5 h-5 bg-blue-400 rounded-full flex items-center justify-center">
                  <span className="text-xs text-white font-bold">i</span>
                </div>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">
                  Demo Instructions
                </h3>
                <div className="mt-1 text-sm text-blue-700">
                  <p>
                    Enter any email and wrong password 3 times to test the 60-second security lockout.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Login Form */}
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              {/* Email Field */}
              <div className="relative group">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white hover:bg-gray-50 focus:bg-white"
                    placeholder="Enter your email"
                    value={formData.email}
                    onChange={handleChange}
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="relative group">
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    className="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 bg-white hover:bg-gray-50 focus:bg-white"
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={handleChange}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Sign in Button */}
            <div>
              <button
                type="submit"
                disabled={isLoading || lockoutInfo.locked}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-xl text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02] hover:shadow-lg"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                    Signing you in...
                  </>
                ) : lockoutInfo.locked ? (
                  <>
                    <Lock className="h-5 w-5 mr-2" />
                    Locked ({lockoutInfo.remainingTime}s)
                  </>
                ) : (
                  <>
                    <span className="relative">
                      Sign in
                      <span className="absolute inset-0 rounded-xl bg-white/20 transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300"></span>
                    </span>
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Additional Links */}
          
        </div>
      </div>
    </div>
  );
}