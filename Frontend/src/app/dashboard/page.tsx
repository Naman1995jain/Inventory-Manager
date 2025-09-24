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
// Removed LineChart — showing product details list instead of activity diagram
import BarChart from '@/components/BarChart';

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalMovements: 0,
    pendingTransfers: 0,
    lowStockItems: 0,
  });
  const [loading, setLoading] = useState(true);
  const [movementSeries, setMovementSeries] = useState<number[]>([]);
  const [movementLabels, setMovementLabels] = useState<string[]>([]);
  const [stockDistribution, setStockDistribution] = useState<{ label: string; value: number }[]>([]);
  const [topLow, setTopLow] = useState<any[]>([]);
  const [topHigh, setTopHigh] = useState<any[]>([]);
  const [pendingTransfersList, setPendingTransfersList] = useState<any[]>([]);
  const [allProducts, setAllProducts] = useState<any[]>([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
  // Get all products to check for low stock (fetch more items for dashboard list)
  const allProductsRes = await productService.getProducts({ page: 1, page_size: 100 });
  setAllProducts(allProductsRes.items || []);
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
            search: 'pending' // search by status value (backend matches status via search)
          })
        ]);

        setStats({
          totalProducts: productsRes.total,
          totalMovements: movementsRes.total,
          pendingTransfers: transfersRes.total,
          lowStockItems: lowStockCount
        });

        // Prepare movement series for last 30 days
        const movementsFull = await stockMovementService.getStockMovements({ page: 1, page_size: 100 });
        const days = 30;
        const dayCounts: Record<string, number> = {};
        const labels: string[] = [];
        for (let i = days - 1; i >= 0; i--) {
          const d = new Date();
          d.setDate(d.getDate() - i);
          const key = d.toISOString().slice(0, 10);
          labels.push(key.slice(5));
          dayCounts[key] = 0;
        }

        movementsFull.items.forEach((m: any) => {
          const day = m.created_at?.slice(0, 10);
          if (day && dayCounts[day] !== undefined) dayCounts[day] += 1;
        });

        setMovementLabels(labels);
        setMovementSeries(labels.map(l => dayCounts[`${new Date().getFullYear()}-${l}`] || 0));

        // Stock distribution: pick top products by total_stock
        const allProducts = allProductsRes.items;
        const sortedByStock = [...allProducts].sort((a, b) => (b.total_stock || 0) - (a.total_stock || 0));
        const distribution = sortedByStock.slice(0, 8).map(p => ({ label: p.name, value: p.total_stock || 0 }));
        setStockDistribution(distribution);

        // Top low / high
        const lowList = [...allProducts].sort((a, b) => (a.total_stock || 0) - (b.total_stock || 0)).slice(0, 5);
        const highList = [...allProducts].sort((a, b) => (b.total_stock || 0) - (a.total_stock || 0)).slice(0, 5);
        setTopLow(lowList);
        setTopHigh(highList);

        // Pending transfers list (few items preview)
  const pendingTransfersFull = await stockTransferService.getStockTransfers({ page: 1, page_size: 20, search: 'pending' });
        setPendingTransfersList(pendingTransfersFull.items || []);
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

          {/* Charts & Details */}
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Products — Quick Details</h3>
              <div className="w-full">
                        {allProducts.length === 0 ? (
                          <div className="text-sm text-gray-500">No product data to show</div>
                        ) : (
                          <div className="space-y-3">
                            {/* Show all fetched products (cap at 100 by fetch) with key details */}
                            {allProducts.map((p) => (
                              <div key={p.id} className="flex items-center justify-between border-b pb-2">
                                <div>
                                  <div className="text-sm font-medium text-gray-900">{p.name}</div>
                                  <div className="text-xs text-gray-500">SKU: {p.sku || 'N/A'} — Unit: {p.unit_of_measure || 'units'}</div>
                                </div>
                                <div className="text-sm font-semibold text-gray-700">{p.total_stock || 0}</div>
                              </div>
                            ))}
                          </div>
                        )}
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Stock distribution (Top products)</h3>
              <BarChart data={stockDistribution} />
            </div>
          </div>

          <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Lowest stock</h3>
              <ul className="space-y-3">
                {topLow.map(p => (
                  <li key={p.id} className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{p.name}</div>
                      <div className="text-xs text-gray-500">SKU: {p.sku}</div>
                    </div>
                    <div className="text-sm font-semibold text-red-600">{p.total_stock || 0}</div>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Highest stock</h3>
              <ul className="space-y-3">
                {topHigh.map(p => (
                  <li key={p.id} className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{p.name}</div>
                      <div className="text-xs text-gray-500">SKU: {p.sku}</div>
                    </div>
                    <div className="text-sm font-semibold text-green-600">{p.total_stock || 0}</div>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Pending transfers</h3>
              {pendingTransfersList.length === 0 ? (
                <div className="text-sm text-gray-500">No pending transfers</div>
              ) : (
                <div className="space-y-3">
                  {pendingTransfersList.map(t => (
                    <div key={t.id} className="flex items-start justify-between">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{t.product?.name || 'Product #' + t.product_id}</div>
                        <div className="text-xs text-gray-500">From: {t.from_warehouse?.name || t.from_warehouse_id} → To: {t.to_warehouse?.name || t.to_warehouse_id}</div>
                      </div>
                      <div className="text-sm font-semibold text-gray-700">{t.quantity}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  </AuthProvider>
  );
}