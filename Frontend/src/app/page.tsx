'use client';

import { AuthProvider } from '@/context/AuthContext';
import { useAuth } from '@/context/AuthContext';
import { Toaster } from 'react-hot-toast';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Landing from '@/components/Landing';

function HomeContent() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          <p className="mt-2 text-sm text-gray-500">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // If not authenticated, show landing page
  if (!isAuthenticated) {
    return <Landing />;
  }

  // If authenticated, show a brief redirect message while navigation happens
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Redirecting to dashboard...</h1>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <AuthProvider>
      <Toaster position="top-right" />
      <HomeContent />
    </AuthProvider>
  );
}