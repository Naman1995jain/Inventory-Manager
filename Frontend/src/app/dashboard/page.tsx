'use client';

import { AuthProvider } from '@/context/AuthContext';
import Layout from '@/components/Layout';
import ProtectedRoute from '@/components/ProtectedRoute';
import WebSocketStatus from '@/components/WebSocketStatus';
import { Toaster } from 'react-hot-toast';
import { Package, BarChart3, ArrowRightLeft, TrendingUp, X } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState, useCallback } from 'react';
import { productService, stockMovementService, stockTransferService } from '@/lib/services';
import { useInstantDashboardUpdates } from '@/hooks/useInstantUpdates';
import toast from 'react-hot-toast';
// Removed LineChart — showing product details list instead of activity diagram
import BarChart from '@/components/BarChart';
import ProductQuickDetails from '@/components/ProductQuickDetails';
import StockListSection from '@/components/StockListSection';
import PurchaseSaleAnalytics from '@/components/PurchaseSaleAnalytics';
import ProductDetailModal from '@/components/ProductDetailModal';

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
  const [deletedProducts, setDeletedProducts] = useState<any[]>([]);
  const [selectedDeletedProduct, setSelectedDeletedProduct] = useState<any>(null);
  const [isDeletedProductModalOpen, setIsDeletedProductModalOpen] = useState(false);
  const [isDeletedProductsListModalOpen, setIsDeletedProductsListModalOpen] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>(new Date().toISOString());

  const fetchDashboardData = useCallback(async () => {
    try {
  // Get all products to check for low stock (fetch more items for dashboard list)
  const allProductsRes = await productService.getProducts({ page: 1, page_size: 20 });
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
        const movementsFull = await stockMovementService.getStockMovements({ page: 1, page_size: 20 });
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

        // Get deleted products
        const deletedProductsRes = await productService.getDeletedProducts({ page: 1, page_size: 20 });
        setDeletedProducts(deletedProductsRes.items || []);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    }, []);

  // WebSocket dashboard updates handler for INSTANT updates
  const handleDashboardUpdate = useCallback((message: any) => {
    console.log('🚀 INSTANT Dashboard Update:', message);
    
    switch (message.type) {
      case 'dashboard_update':
        if (message.update_type === 'stock_movement') {
          // Instantly refresh dashboard data
          fetchDashboardData();
          toast.success('📊 Stock movement - Dashboard updated!', { duration: 2000 });
        } else if (message.update_type === 'stock_transfer') {
          fetchDashboardData();
          toast.success('🔄 Stock transfer - Dashboard updated!', { duration: 2000 });
        }
        break;
        
      case 'dashboard_stats_update':
        // Instantly update specific stats
        setStats(prevStats => ({
          ...prevStats,
          ...message.data
        }));
        toast.success('⚡ Stats updated instantly!', { duration: 1500 });
        break;
    }
    
    setLastUpdate(new Date().toISOString());
  }, []);

  // Subscribe to INSTANT dashboard updates
  useInstantDashboardUpdates(handleDashboardUpdate);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return (
    <AuthProvider>
      <ProtectedRoute>
        <Layout>
          <Toaster position="top-right" />
          <WebSocketStatus showText={false} />
          <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">Dashboard</h1>
                <p className="mt-1 text-sm text-gray-600">
                  Overview of your inventory management system
                  {lastUpdate && (
                    <span className="block text-xs text-gray-500 mt-1 sm:inline sm:ml-2 sm:mt-0">
                      Last updated: {new Date(lastUpdate).toLocaleTimeString()}
                    </span>
                  )}
                </p>
              </div>
            </div>

            {/* Stats Cards - Mobile-first responsive grid */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:shadow-md transition-shadow duration-200">
                <div className="p-4 sm:p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-blue-100">
                        <Package className="h-5 w-5 text-blue-600" />
                      </div>
                    </div>
                    <div className="ml-4 flex-1 min-w-0">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Total Products
                        </dt>
                        <dd className="text-xl font-bold text-gray-900 sm:text-2xl">
                          {loading ? (
                            <div className="h-6 w-8 bg-gray-200 animate-pulse rounded"></div>
                          ) : (
                            stats.totalProducts
                          )}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-4 py-2 sm:px-5 sm:py-3">
                  <Link 
                    href="/products" 
                    className="text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center justify-between group"
                  >
                    View all
                    <span className="ml-2 group-hover:translate-x-1 transition-transform duration-200">→</span>
                  </Link>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:shadow-md transition-shadow duration-200">
                <div className="p-4 sm:p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-green-100">
                        <BarChart3 className="h-5 w-5 text-green-600" />
                      </div>
                    </div>
                    <div className="ml-4 flex-1 min-w-0">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Stock Movements
                        </dt>
                        <dd className="text-xl font-bold text-gray-900 sm:text-2xl">
                          {loading ? (
                            <div className="h-6 w-8 bg-gray-200 animate-pulse rounded"></div>
                          ) : (
                            stats.totalMovements
                          )}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-4 py-2 sm:px-5 sm:py-3">
                  <Link 
                    href="/stock-movements" 
                    className="text-sm font-medium text-green-600 hover:text-green-800 flex items-center justify-between group"
                  >
                    View all
                    <span className="ml-2 group-hover:translate-x-1 transition-transform duration-200">→</span>
                  </Link>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:shadow-md transition-shadow duration-200">
                <div className="p-4 sm:p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-orange-100">
                        <ArrowRightLeft className="h-5 w-5 text-orange-600" />
                      </div>
                    </div>
                    <div className="ml-4 flex-1 min-w-0">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Pending Transfers
                        </dt>
                        <dd className="text-xl font-bold text-gray-900 sm:text-2xl">
                          {loading ? (
                            <div className="h-6 w-8 bg-gray-200 animate-pulse rounded"></div>
                          ) : (
                            stats.pendingTransfers
                          )}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-4 py-2 sm:px-5 sm:py-3">
                  <Link 
                    href="/stock-transfers" 
                    className="text-sm font-medium text-orange-600 hover:text-orange-800 flex items-center justify-between group"
                  >
                    View all
                    <span className="ml-2 group-hover:translate-x-1 transition-transform duration-200">→</span>
                  </Link>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:shadow-md transition-shadow duration-200">
                <div className="p-4 sm:p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-red-100">
                        <TrendingUp className="h-5 w-5 text-red-600" />
                      </div>
                    </div>
                    <div className="ml-4 flex-1 min-w-0">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Low Stock Items
                        </dt>
                        <dd className="text-xl font-bold text-gray-900 sm:text-2xl">
                          {loading ? (
                            <div className="h-6 w-8 bg-gray-200 animate-pulse rounded"></div>
                          ) : (
                            stats.lowStockItems
                          )}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-4 py-2 sm:px-5 sm:py-3">
                  <Link 
                    href="/products" 
                    className="text-sm font-medium text-red-600 hover:text-red-800 flex items-center justify-between group"
                  >
                    View all
                    <span className="ml-2 group-hover:translate-x-1 transition-transform duration-200">→</span>
                  </Link>
                </div>
              </div>
            </div>

            {/* Quick Actions - Improved mobile layout */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 sm:gap-4">
                <Link
                  href="/products/new"
                  className="group relative flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
                >
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-blue-100 group-hover:bg-blue-200 transition-colors duration-200">
                      <Package className="h-5 w-5 text-blue-600" />
                    </div>
                    <span className="text-sm font-medium text-gray-900 group-hover:text-blue-800">
                      Add New Product
                    </span>
                  </div>
                </Link>

                <Link
                  href="/stock-movements/new"
                  className="group relative flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-400 hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200"
                >
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-green-100 group-hover:bg-green-200 transition-colors duration-200">
                      <BarChart3 className="h-5 w-5 text-green-600" />
                    </div>
                    <span className="text-sm font-medium text-gray-900 group-hover:text-green-800">
                      Record Movement
                    </span>
                  </div>
                </Link>

                <Link
                  href="/stock-transfers/new"
                  className="group relative flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-orange-400 hover:bg-orange-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-all duration-200 sm:col-span-2 lg:col-span-1"
                >
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-orange-100 group-hover:bg-orange-200 transition-colors duration-200">
                      <ArrowRightLeft className="h-5 w-5 text-orange-600" />
                    </div>
                    <span className="text-sm font-medium text-gray-900 group-hover:text-orange-800">
                      Create Transfer
                    </span>
                  </div>
                </Link>
              </div>
            </div>

            {/* Charts & Details - Mobile responsive */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <ProductQuickDetails products={allProducts} maxItems={5} />
              </div>

              <div className="bg-white p-4 sm:p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Stock Distribution</h3>
                <div className="h-64 sm:h-80 flex items-center justify-center">
                  <BarChart data={stockDistribution} />
                </div>
              </div>
            </div>

            {/* Stock Lists - Mobile responsive */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <StockListSection 
                products={topLow} 
                title="Lowest Stock" 
                type="low" 
                maxItems={4} 
              />

              <StockListSection 
                products={topHigh} 
                title="Highest Stock" 
                type="high" 
                maxItems={4} 
              />

              <div className="bg-white p-4 sm:p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Pending Transfers</h3>
                {pendingTransfersList.length === 0 ? (
                  <div className="text-center py-8">
                    <ArrowRightLeft className="mx-auto h-12 w-12 text-gray-300" />
                    <p className="mt-2 text-sm text-gray-500">No pending transfers</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {pendingTransfersList.map(t => (
                      <div key={t.id} className="flex items-start justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-gray-900 truncate">
                            {t.product?.name || 'Product #' + t.product_id}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            <span className="block sm:inline">From: {t.from_warehouse?.name || t.from_warehouse_id}</span>
                            <span className="hidden sm:inline mx-1">→</span>
                            <span className="block sm:inline">To: {t.to_warehouse?.name || t.to_warehouse_id}</span>
                          </div>
                        </div>
                        <div className="ml-3 flex-shrink-0">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                            {t.quantity}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Purchase & Sale Analytics */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
              <PurchaseSaleAnalytics />
            </div>

            {/* Deleted Products */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Deleted Products</h3>
                {deletedProducts.length > 4 && (
                  <button
                    onClick={() => setIsDeletedProductsListModalOpen(true)}
                    className="text-sm font-medium text-red-600 hover:text-red-800 flex items-center group"
                  >
                    View all ({deletedProducts.length})
                    <span className="ml-1 group-hover:translate-x-1 transition-transform duration-200">→</span>
                  </button>
                )}
              </div>
              {deletedProducts.length === 0 ? (
                <div className="text-center py-8">
                  <Package className="mx-auto h-12 w-12 text-gray-300" />
                  <p className="mt-2 text-sm text-gray-500">No deleted products</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {deletedProducts.slice(0, 4).map(product => (
                    <div 
                      key={product.id} 
                      className="flex items-start justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                      onClick={() => {
                        setSelectedDeletedProduct(product);
                        setIsDeletedProductModalOpen(true);
                      }}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-900 truncate">
                          {product.name}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          SKU: {product.sku}
                        </div>
                        {product.deleted_at && (
                          <div className="text-xs text-red-500 mt-1">
                            Deleted: {new Date(product.deleted_at).toLocaleDateString()}
                          </div>
                        )}
                      </div>
                      <div className="ml-3 flex-shrink-0">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Deleted
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Deleted Product Detail Modal */}
          {selectedDeletedProduct && (
            <ProductDetailModal
              product={selectedDeletedProduct}
              isOpen={isDeletedProductModalOpen}
              onClose={() => {
                setIsDeletedProductModalOpen(false);
                setSelectedDeletedProduct(null);
              }}
            />
          )}

          {/* Deleted Products List Modal */}
          {isDeletedProductsListModalOpen && (
            <div className="fixed inset-0 z-50 overflow-y-auto">
              <div className="flex min-h-screen items-center justify-center p-2 sm:p-4">
                {/* Backdrop */}
                <div 
                  className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
                  onClick={() => setIsDeletedProductsListModalOpen(false)}
                />
                
                {/* Modal */}
                <div className="relative bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                  {/* Header */}
                  <div className="flex items-center justify-between p-3 sm:p-6 border-b border-gray-200">
                    <div className="flex items-center space-x-2 sm:space-x-3">
                      <Package className="h-5 w-5 sm:h-6 sm:w-6 text-red-600" />
                      <h2 className="text-lg sm:text-xl font-semibold text-gray-900">
                        Deleted Products ({deletedProducts.length})
                      </h2>
                    </div>
                    <button
                      onClick={() => setIsDeletedProductsListModalOpen(false)}
                      className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      <X className="h-5 w-5 sm:h-6 sm:w-6" />
                    </button>
                  </div>

                  {/* Content */}
                  <div className="p-3 sm:p-6">
                    {deletedProducts.length === 0 ? (
                      <div className="text-center py-8">
                        <Package className="mx-auto h-12 w-12 text-gray-300" />
                        <p className="mt-2 text-sm text-gray-500">No deleted products</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 gap-3 sm:gap-4">
                        {deletedProducts.map(product => (
                          <div 
                            key={product.id} 
                            className="flex items-start justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors border border-gray-200"
                            onClick={() => {
                              setSelectedDeletedProduct(product);
                              setIsDeletedProductModalOpen(true);
                              setIsDeletedProductsListModalOpen(false);
                            }}
                          >
                            <div className="flex-1 min-w-0">
                              <div className="text-sm font-medium text-gray-900 truncate">
                                {product.name}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">
                                SKU: {product.sku}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">
                                Category: {product.category || 'Uncategorized'}
                              </div>
                              {product.deleted_at && (
                                <div className="text-xs text-red-500 mt-1">
                                  Deleted: {new Date(product.deleted_at).toLocaleDateString()}
                                </div>
                              )}
                            </div>
                            <div className="ml-3 flex-shrink-0">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                Deleted
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
      </Layout>
    </ProtectedRoute>
  </AuthProvider>
  );
}