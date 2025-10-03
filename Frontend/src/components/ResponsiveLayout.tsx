'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { 
  Package, 
  BarChart3, 
  ArrowRightLeft, 
  User, 
  LogOut,
  Home,
  Menu,
  X,
  ChevronDown,
  Settings,
  Bell,
  Search
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export default function ResponsiveLayout({ children }: LayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { user, logout, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    logout();
    router.push('/login');
    setUserMenuOpen(false);
    setMobileOpen(false);
  };

  // Close mobile menu when route changes
  useEffect(() => {
    setMobileOpen(false);
    setUserMenuOpen(false);
  }, [pathname]);

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (mobileOpen || userMenuOpen) {
        setMobileOpen(false);
        setUserMenuOpen(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [mobileOpen, userMenuOpen]);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Products', href: '/products', icon: Package },
    { name: 'Stock Movements', href: '/stock-movements', icon: BarChart3 },
    { name: 'Stock Transfers', href: '/stock-transfers', icon: ArrowRightLeft },
  ];

  const isCurrentPath = (href: string) => pathname === href;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-blue-200 border-t-blue-600"></div>
          <p className="mt-4 text-sm text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile navigation backdrop */}
      {mobileOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 shadow-lg border-r border-gray-200">
          {/* Logo */}
          <div className="flex h-16 shrink-0 items-center">
            <Package className="h-8 w-8 text-blue-600" />
            <span className="ml-2 text-xl font-bold text-gray-900">Inventory</span>
          </div>
          
          {/* Navigation */}
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => {
                    const Icon = item.icon;
                    return (
                      <li key={item.name}>
                        <Link
                          href={item.href}
                          className={`
                            group flex gap-x-3 rounded-md p-3 text-sm leading-6 font-medium transition-all duration-200
                            ${isCurrentPath(item.href)
                              ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                              : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                            }
                          `}
                        >
                          <Icon className={`h-5 w-5 shrink-0 ${isCurrentPath(item.href) ? 'text-blue-600' : 'text-gray-400 group-hover:text-blue-600'}`} />
                          {item.name}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </li>
            </ul>
          </nav>

          {/* User section */}
          <div className="border-t border-gray-200 pt-4">
            <div className="relative">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setUserMenuOpen(!userMenuOpen);
                }}
                className="flex w-full items-center gap-x-3 rounded-md p-3 text-sm leading-6 font-medium text-gray-700 hover:bg-gray-50 transition-all duration-200"
              >
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100">
                  <User className="h-4 w-4 text-blue-600" />
                </div>
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium text-gray-900">{user?.email || 'User'}</p>
                  <p className="text-xs text-gray-500 capitalize">{user?.is_admin ? 'Admin' : 'User'}</p>
                </div>
                <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform duration-200 ${userMenuOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* User dropdown */}
              {userMenuOpen && (
                <div className="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-md shadow-lg border border-gray-200 py-1">
                  <Link
                    href="/profile"
                    className="flex items-center gap-x-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <Settings className="h-4 w-4 text-gray-400" />
                    Profile Settings
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-x-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <LogOut className="h-4 w-4 text-gray-400" />
                    Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Mobile navigation */}
      <div className={`fixed inset-y-0 left-0 z-50 w-80 transform bg-white shadow-xl transition-transform duration-300 ease-in-out lg:hidden ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex h-full flex-col">
          {/* Mobile header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex items-center">
              <Package className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">Inventory</span>
            </div>
            <button
              onClick={() => setMobileOpen(false)}
              className="rounded-md p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all duration-200"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Mobile navigation content */}
          <div className="flex-1 overflow-y-auto px-4 py-6">
            <nav className="space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`
                      group flex items-center gap-x-3 rounded-xl p-4 text-base font-medium transition-all duration-200
                      ${isCurrentPath(item.href)
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon className={`h-6 w-6 shrink-0 ${isCurrentPath(item.href) ? 'text-blue-600' : 'text-gray-400 group-hover:text-blue-600'}`} />
                    {item.name}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Mobile user section */}
          <div className="border-t border-gray-200 p-4">
            <div className="space-y-2">
              <div className="flex items-center gap-x-3 rounded-xl p-4 bg-gray-50">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100">
                  <User className="h-5 w-5 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{user?.email || 'User'}</p>
                  <p className="text-xs text-gray-500 capitalize">{user?.is_admin ? 'Admin' : 'User'}</p>
                </div>
              </div>
              
              <Link
                href="/profile"
                className="flex items-center gap-x-3 rounded-xl p-4 text-gray-700 hover:bg-gray-50 transition-all duration-200"
              >
                <Settings className="h-5 w-5 text-gray-400" />
                <span className="text-sm font-medium">Profile Settings</span>
              </Link>
              
              <button
                onClick={handleLogout}
                className="flex w-full items-center gap-x-3 rounded-xl p-4 text-gray-700 hover:bg-gray-50 transition-all duration-200"
              >
                <LogOut className="h-5 w-5 text-gray-400" />
                <span className="text-sm font-medium">Sign out</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Top bar for mobile */}
      <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:hidden">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setMobileOpen(true);
          }}
          className="rounded-md p-2.5 text-gray-700 hover:text-gray-900 hover:bg-gray-100 transition-all duration-200"
        >
          <Menu className="h-6 w-6" />
        </button>
        
        <div className="flex flex-1 items-center justify-between">
          <div className="flex items-center">
            <Package className="h-7 w-7 text-blue-600" />
            <span className="ml-2 text-lg font-bold text-gray-900">Inventory</span>
          </div>
          
          <div className="flex items-center gap-x-2">
            {/* Search button for mobile */}
            <button className="rounded-full p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all duration-200">
              <Search className="h-5 w-5" />
            </button>
            
            {/* Notification bell */}
            <button className="rounded-full p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all duration-200">
              <Bell className="h-5 w-5" />
            </button>
            
            {/* Mobile user avatar */}
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100">
              <User className="h-4 w-4 text-blue-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-72">
        <main className="py-4 px-4 sm:py-6 sm:px-6 lg:px-8">
          {children}
        </main>
      </div>
    </div>
  );
}