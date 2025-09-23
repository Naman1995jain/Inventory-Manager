'use client';

import { AuthProvider } from '@/context/AuthContext';
import Layout from '@/components/Layout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Toaster } from 'react-hot-toast';
import { Package, BarChart3, ArrowRightLeft, TrendingUp } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { productService, stockMovementService, stockTransferService } from '@/lib/services';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalMovements: 0,
    pendingTransfers: 0,
    lowStockItems: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Get all products to check for low stock
        const allProductsRes = await productService.getProducts({ page: 1, page_size: 20 });
        const lowStockCount = allProductsRes.items.filter(product => 
          (product.total_stock || 0) < 10
        ).length;

        // Get total counts using search parameters
        const [productsRes, movementsRes, transfersRes] = await Promise.all([
          productService.getProducts({ page: 1, page_size: 1 }), // Just to get total count
          stockMovementService.getStockMovements({ page: 1, page_size: 1 }), // Just to get total count
          stockTransferService.getStockTransfers({ 
            page: 1, 
            page_size: 1,
            search: 'status:pending' // Using search to filter pending transfers
          })
        ]);

        setStats({
          totalProducts: productsRes.total,
          totalMovements: movementsRes.total,
          pendingTransfers: transfersRes.total,
          lowStockItems: lowStockCount
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <AuthProvider>
      <ProtectedRoute>
        <Layout>
          <Toaster position="top-right" />
          <div className="px-4 sm:px-6 lg:px-8">
            <div className="sm:flex sm:items-center">
              <div className="sm:flex-auto">
                <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
                <p className="mt-2 text-sm text-gray-700">
                  Overview of your inventory management system
                </p>
              </div>
            </div>

          {/* Stats Cards */}
          <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Package className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total Products
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {loading ? '-' : stats.totalProducts}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-5 py-3">
                <div className="text-sm">
                  <Link href="/products" className="font-medium text-indigo-700 hover:text-indigo-900">
                    View all
                  </Link>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <BarChart3 className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Stock Movements
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {loading ? '-' : stats.totalMovements}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-5 py-3">
                <div className="text-sm">
                  <Link href="/stock-movements" className="font-medium text-indigo-700 hover:text-indigo-900">
                    View all
                  </Link>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ArrowRightLeft className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Pending Transfers
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {loading ? '-' : stats.pendingTransfers}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-5 py-3">
                <div className="text-sm">
                  <Link href="/stock-transfers" className="font-medium text-indigo-700 hover:text-indigo-900">
                    View all
                  </Link>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <TrendingUp className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Low Stock Items
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {loading ? '-' : stats.lowStockItems}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-5 py-3">
                <div className="text-sm">
                  <Link href="/products" className="font-medium text-indigo-700 hover:text-indigo-900">
                    View all
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mt-8">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <Link
                href="/products/new"
                className="relative block w-full border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <Package className="mx-auto h-12 w-12 text-gray-400" />
                <span className="mt-2 block text-sm font-medium text-gray-900">
                  Add New Product
                </span>
              </Link>

              <Link
                href="/stock-movements/new"
                className="relative block w-full border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
                <span className="mt-2 block text-sm font-medium text-gray-900">
                  Record Stock Movement
                </span>
              </Link>

              <Link
                href="/stock-transfers/new"
                className="relative block w-full border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <ArrowRightLeft className="mx-auto h-12 w-12 text-gray-400" />
                <span className="mt-2 block text-sm font-medium text-gray-900">
                  Create Stock Transfer
                </span>
              </Link>
            </div>
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  </AuthProvider>
  );
}