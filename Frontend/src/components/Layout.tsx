'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Package, 
  BarChart3, 
  ArrowRightLeft, 
  User, 
  LogOut,
  Home,
  Menu,
  X
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, logout, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // Show loading if auth is being checked
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          <p className="mt-2 text-sm text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Package className="h-8 w-8 text-indigo-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">
                  Inventory Manager
                </span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                  href="/dashboard"
                  className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm inline-flex items-center"
                >
                  <Home className="h-4 w-4 mr-1" />
                  Dashboard
                </Link>
                <Link
                  href="/products"
                  className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm inline-flex items-center"
                >
                  <Package className="h-4 w-4 mr-1" />
                  Products
                </Link>
                <Link
                  href="/stock-movements"
                  className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm inline-flex items-center"
                >
                  <BarChart3 className="h-4 w-4 mr-1" />
                  Stock Movements
                </Link>
                <Link
                  href="/stock-transfers"
                  className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm inline-flex items-center"
                >
                  <ArrowRightLeft className="h-4 w-4 mr-1" />
                  Stock Transfers
                </Link>
              </div>
            </div>
            {/* Mobile menu button */}
            <div className="flex items-center sm:hidden">
              <button
                onClick={() => setMobileOpen(!mobileOpen)}
                aria-expanded={mobileOpen}
                className="p-2 rounded-md text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>

            <div className="hidden sm:ml-6 sm:flex sm:items-center">
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <User className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-700">{user?.email}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="bg-white p-1 rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile dropdown menu */}
      {mobileOpen && (
        <>
          <div className="sm:hidden fixed inset-0 z-40" onClick={() => setMobileOpen(false)}></div>
          <div className="sm:hidden fixed top-16 right-4 z-50 w-64 bg-white border rounded-lg shadow-lg">
            <div className="p-4 space-y-3">
              <Link href="/dashboard" className="flex items-center px-2 py-2 rounded hover:bg-gray-50 text-gray-700">
                <Home className="h-4 w-4 mr-2" /> Dashboard
              </Link>
              <Link href="/products" className="flex items-center px-2 py-2 rounded hover:bg-gray-50 text-gray-700">
                <Package className="h-4 w-4 mr-2" /> Products
              </Link>
              <Link href="/stock-movements" className="flex items-center px-2 py-2 rounded hover:bg-gray-50 text-gray-700">
                <BarChart3 className="h-4 w-4 mr-2" /> Stock Movements
              </Link>
              <Link href="/stock-transfers" className="flex items-center px-2 py-2 rounded hover:bg-gray-50 text-gray-700">
                <ArrowRightLeft className="h-4 w-4 mr-2" /> Stock Transfers
              </Link>
              <div className="border-t pt-2">
                <div className="flex items-center px-2 py-2 text-sm text-gray-700">
                  <User className="h-4 w-4 mr-2 text-gray-400" /> {user?.email}
                </div>
                <button onClick={() => { setMobileOpen(false); handleLogout(); }} className="w-full text-left px-2 py-2 text-sm text-red-600 hover:bg-gray-50">
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}