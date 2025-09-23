'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { UserLogin } from '@/types';
import LoginSecurityManager from '@/lib/loginSecurity';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function LoginForm() {
  const [formData, setFormData] = useState<UserLogin>({
    email: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
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
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link href="/register" className="font-medium text-indigo-600 hover:text-indigo-500">
              create a new account
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {/* Lockout Warning */}
          {lockoutInfo.locked && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    Account Temporarily Locked
                  </h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>
                      Too many failed login attempts. Please wait{' '}
                      <span className="font-semibold">{lockoutInfo.remainingTime}</span> seconds before trying again.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Demo instructions */}
          <div className="rounded-md bg-blue-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">
                  Demo Instructions
                </h3>
                <div className="mt-2 text-sm text-blue-700">
                  <p>
                    To test the security feature: Enter any email and wrong password 3 times to trigger the 60-second lockout.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={formData.email}
                onChange={handleChange}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading || lockoutInfo.locked}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Signing in...
                </>
              ) : lockoutInfo.locked ? (
                `Locked (${lockoutInfo.remainingTime}s)`
              ) : (
                'Sign in'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}