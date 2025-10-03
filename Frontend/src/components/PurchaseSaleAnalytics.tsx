'use client';

import React, { useState, useEffect } from 'react';
import { StockMovement } from '@/types';
import { stockMovementService } from '@/lib/services';
import { TrendingUp, TrendingDown, DollarSign, Package, Calendar, Info } from 'lucide-react';
import LineChart from './LineChart';
import BarChart from './BarChart';
import TransactionsModal from './TransactionsModal';
import toast from 'react-hot-toast';
import { format, startOfMonth, endOfMonth, parseISO } from 'date-fns';

interface PurchaseSaleAnalyticsProps {
  className?: string;
}

interface PurchaseSaleData {
  totalPurchases: number;
  totalSales: number;
  totalPurchaseValue: number;
  totalSaleValue: number;
  recentTransactions: StockMovement[];
  monthlyData: {
    month: string;
    purchases: number;
    sales: number;
    purchaseValue: number;
    saleValue: number;
  }[];
  topProducts: {
    name: string;
    totalQuantity: number;
    totalValue: number;
    type: 'purchase' | 'sale';
  }[];
}

export default function PurchaseSaleAnalytics({ className = '' }: PurchaseSaleAnalyticsProps) {
  const [data, setData] = useState<PurchaseSaleData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedView, setSelectedView] = useState<'quantity' | 'value'>('quantity');
  const [isTransactionsModalOpen, setIsTransactionsModalOpen] = useState(false);

  useEffect(() => {
    fetchPurchaseSaleData();
  }, []);

  const fetchPurchaseSaleData = async () => {
    try {
      setIsLoading(true);
      const response = await stockMovementService.getPurchaseSaleMovements();
      const movements = response.items;

      // Calculate totals
      const purchases = movements.filter(m => m.movement_type === 'purchase');
      const sales = movements.filter(m => m.movement_type === 'sale');

      const totalPurchases = purchases.reduce((sum, m) => sum + Math.abs(m.quantity), 0);
      const totalSales = sales.reduce((sum, m) => sum + Math.abs(m.quantity), 0);
      const totalPurchaseValue = purchases.reduce((sum, m) => sum + (m.total_cost || 0), 0);
      const totalSaleValue = sales.reduce((sum, m) => sum + Math.abs(m.total_cost || 0), 0);

      // Get recent transactions (last 10)
      const recentTransactions = movements.slice(0, 10);

      // Calculate monthly data (last 6 months)
      const monthlyData = calculateMonthlyData(movements);

      // Calculate top products
      const topProducts = calculateTopProducts(movements);

      setData({
        totalPurchases,
        totalSales,
        totalPurchaseValue,
        totalSaleValue,
        recentTransactions,
        monthlyData,
        topProducts
      });
    } catch (error) {
      toast.error('Failed to fetch purchase/sale data');
      console.error('Error fetching purchase/sale data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateMonthlyData = (movements: any[]) => {
    const monthlyMap = new Map();
    const now = new Date();
    
    // Initialize last 6 months
    for (let i = 5; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthKey = format(date, 'yyyy-MM');
      monthlyMap.set(monthKey, {
        month: format(date, 'MMM yyyy'),
        purchases: 0,
        sales: 0,
        purchaseValue: 0,
        saleValue: 0
      });
    }

    // Aggregate movements by month
    movements.forEach(movement => {
      const createdAt = parseISO(movement.created_at);
      const monthKey = format(createdAt, 'yyyy-MM');
      
      if (monthlyMap.has(monthKey)) {
        const data = monthlyMap.get(monthKey);
        if (movement.movement_type === 'purchase') {
          data.purchases += Math.abs(movement.quantity);
          data.purchaseValue += movement.total_cost || 0;
        } else if (movement.movement_type === 'sale') {
          data.sales += Math.abs(movement.quantity);
          data.saleValue += Math.abs(movement.total_cost || 0);
        }
      }
    });

    return Array.from(monthlyMap.values());
  };

  const calculateTopProducts = (movements: any[]) => {
    const productMap = new Map();

    movements.forEach(movement => {
      const productName = movement.product_name || `Product ${movement.product_id}`;
      const key = `${productName}-${movement.movement_type}`;
      
      if (!productMap.has(key)) {
        productMap.set(key, {
          name: productName,
          totalQuantity: 0,
          totalValue: 0,
          type: movement.movement_type
        });
      }

      const data = productMap.get(key);
      data.totalQuantity += Math.abs(movement.quantity);
      data.totalValue += Math.abs(movement.total_cost || 0);
    });

    return Array.from(productMap.values())
      .sort((a, b) => b.totalValue - a.totalValue)
      .slice(0, 8);
  };

  // Safely format unit cost for display. Accepts numbers, numeric strings, or null/undefined.
  const formatUnitCost = (value: any) => {
    if (value === null || value === undefined) return null;
    const num = Number(value);
    if (Number.isNaN(num)) return null;
    return num.toFixed(2);
  };

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-40 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
        <div className="text-center text-gray-500">
          <Package className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <p>No purchase/sale data available</p>
        </div>
      </div>
    );
  }

  const chartData = selectedView === 'quantity' 
    ? data.monthlyData.map(d => d.purchases + d.sales)
    : data.monthlyData.map(d => d.purchaseValue + d.saleValue);

  const chartLabels = data.monthlyData.map(d => d.month);

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Recent Transactions</h3>
      </div>

      <div className="p-6">
        {/* Recent Transactions */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-md font-medium text-gray-900">Purchase & Sale</h4>
            {data.recentTransactions.length > 4 && (
              <button
                onClick={() => setIsTransactionsModalOpen(true)}
                className="text-sm text-indigo-600 hover:text-indigo-500 font-medium"
              >
                View All ({data.recentTransactions.length})
              </button>
            )}
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            {data.recentTransactions.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No recent transactions</p>
            ) : (
              <div className="space-y-4">
                {data.recentTransactions.slice(0, 4).map((transaction, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-3 sm:p-4 hover:bg-gray-50 transition-colors">
                    {/* Mobile Layout */}
                    <div className="block sm:hidden">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-start space-x-3 flex-1">
                          <div className="flex-shrink-0">
                            {transaction.movement_type === 'purchase' ? (
                              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                                <TrendingUp className="h-4 w-4 text-green-600" />
                              </div>
                            ) : (
                              <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                                <TrendingDown className="h-4 w-4 text-red-600" />
                              </div>
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <h4 className="text-sm font-semibold text-gray-900 truncate">
                              {transaction.product?.name || transaction.product_name || `Product ${transaction.product_id}`}
                            </h4>
                            <p className="text-xs text-gray-500 mt-1">
                              {format(parseISO(transaction.created_at), 'MMM dd, HH:mm')}
                            </p>
                          </div>
                        </div>
                        <div className="flex flex-col items-end space-y-1">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                            transaction.movement_type === 'purchase'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {transaction.movement_type === 'purchase' ? '+' : '-'}{Math.abs(transaction.quantity)}
                          </span>
                          <span className="text-xs text-gray-600">
                            ${Math.abs(transaction.total_cost || 0).toLocaleString()}
                          </span>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 gap-1 text-xs text-gray-600 mb-2">
                        <div className="flex items-center justify-between">
                          <span>SKU:</span>
                          <span>{transaction.product?.sku || 'N/A'}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Category:</span>
                          <span>{transaction.product?.category || 'N/A'}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Warehouse:</span>
                          <span className="truncate ml-2">{transaction.warehouse?.name || transaction.warehouse_name || `Warehouse ${transaction.warehouse_id}`}</span>
                        </div>
                        {formatUnitCost(transaction.unit_cost) !== null && (
                          <div className="flex items-center justify-between">
                            <span>Unit Cost:</span>
                            <span>${formatUnitCost(transaction.unit_cost)}</span>
                          </div>
                        )}
                      </div>

                      {transaction.notes && (
                        <div className="text-xs text-gray-600 bg-gray-100 p-2 rounded mt-2">
                          <span className="font-medium">Notes:</span> {transaction.notes}
                        </div>
                      )}
                    </div>

                    {/* Desktop Layout */}
                    <div className="hidden sm:block">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-4 flex-1">
                          <div className="flex-shrink-0">
                            {transaction.movement_type === 'purchase' ? (
                              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                                <TrendingUp className="h-5 w-5 text-green-600" />
                              </div>
                            ) : (
                              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                                <TrendingDown className="h-5 w-5 text-red-600" />
                              </div>
                            )}
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="text-sm font-semibold text-gray-900">
                                {transaction.product?.name || transaction.product_name || `Product ${transaction.product_id}`}
                              </h4>
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                transaction.movement_type === 'purchase'
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-red-100 text-red-800'
                              }`}>
                                {transaction.movement_type.toUpperCase()}
                              </span>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-gray-600 mb-2">
                              <div className="flex items-center space-x-1">
                                <Package className="h-3 w-3" />
                                <span>SKU: {transaction.product?.sku || 'N/A'}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Calendar className="h-3 w-3" />
                                <span>{format(parseISO(transaction.created_at), 'MMM dd, yyyy HH:mm')}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Package className="h-3 w-3" />
                                <span>Category: {transaction.product?.category || 'N/A'}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <DollarSign className="h-3 w-3" />
                                <span>Unit: {transaction.product?.unit_of_measure || 'units'}</span>
                              </div>
                            </div>

                            <div className="text-xs text-gray-600 mb-2">
                              <div className="flex items-center space-x-1 mb-1">
                                <span className="font-medium">Warehouse:</span>
                                <span>{transaction.warehouse?.name || transaction.warehouse_name || `Warehouse ${transaction.warehouse_id}`}</span>
                                {transaction.warehouse?.location && (
                                  <span className="text-gray-500">({transaction.warehouse.location})</span>
                                )}
                              </div>
                              {transaction.reference_number && (
                                <div className="flex items-center space-x-1 mb-1">
                                  <span className="font-medium">Ref:</span>
                                  <span>{transaction.reference_number}</span>
                                </div>
                              )}
                              <div className="flex items-center space-x-1">
                                <span className="font-medium">Created by:</span>
                                <span>{transaction.creator?.email || 'Unknown'}</span>
                              </div>
                            </div>

                            {transaction.notes && (
                              <div className="text-xs text-gray-600 bg-gray-100 p-2 rounded mt-2">
                                <span className="font-medium">Notes:</span> {transaction.notes}
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="flex flex-col items-end space-y-1 ml-4">
                          <div className={`text-lg font-bold ${
                            transaction.movement_type === 'purchase' ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {transaction.movement_type === 'purchase' ? '+' : '-'}{Math.abs(transaction.quantity)}
                          </div>
                          <div className="text-sm text-gray-600">
                            ${Math.abs(transaction.total_cost || 0).toLocaleString()}
                          </div>
                          {formatUnitCost(transaction.unit_cost) !== null && (
                            <div className="text-xs text-gray-500">
                              ${formatUnitCost(transaction.unit_cost)}/unit
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {data.recentTransactions.length > 4 && (
              <div className="mt-4 text-center">
                <button
                  onClick={() => setIsTransactionsModalOpen(true)}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-md hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                >
                  <Info className="h-4 w-4 mr-1" />
                  <span className="hidden sm:inline">View All Transactions</span>
                  <span className="sm:hidden">View All ({data?.recentTransactions?.length || 0})</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Transactions Modal */}
      <TransactionsModal
        transactions={data.recentTransactions}
        isOpen={isTransactionsModalOpen}
        onClose={() => setIsTransactionsModalOpen(false)}
      />
    </div>
  );
}