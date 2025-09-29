'use client';

import React, { useState, useEffect } from 'react';
import { StockTransfer, StockTransferListResponse } from '@/types';
import { stockTransferService } from '@/lib/services';
import { useAuth } from '@/context/AuthContext';
import { Search, Plus, ArrowRight, CheckCircle, XCircle, Clock, ArrowRightLeft } from 'lucide-react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

export default function StockTransferList() {
  const { user } = useAuth();
  const [transfers, setTransfers] = useState<StockTransfer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  // Helper function to check if current user can edit this transfer
  const canEditTransfer = (transfer: StockTransfer) => {
    return user && transfer.created_by === user.id;
  };

  const fetchTransfers = async () => {
    try {
      setIsLoading(true);
      const response: StockTransferListResponse = await stockTransferService.getStockTransfers({
        page,
        page_size: 20,
        search: search || undefined,
        sort_by: 'created_desc'
      });
      
      setTransfers(response.items);
      setTotalPages(response.total_pages);
      setTotal(response.total);
    } catch (error) {
      toast.error('Failed to fetch stock transfers');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTransfers();
  }, [page, search]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchTransfers();
  };

  const handleCompleteTransfer = async (transferId: number) => {
    try {
      await stockTransferService.completeStockTransfer(transferId);
      toast.success('Transfer completed successfully');
      fetchTransfers(); // Refresh the list
    } catch (error) {
      toast.error('Failed to complete transfer');
    }
  };

  const handleCancelTransfer = async (transferId: number) => {
    try {
      await stockTransferService.cancelStockTransfer(transferId);
      toast.success('Transfer cancelled successfully');
      fetchTransfers(); // Refresh the list
    } catch (error) {
      toast.error('Failed to cancel transfer');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";
    switch (status) {
      case 'pending':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'completed':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'cancelled':
        return `${baseClasses} bg-red-100 text-red-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  if (isLoading && transfers.length === 0) {
    return (
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded"></div>
          <div className="h-12 bg-gray-200 rounded"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Stock Transfers</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage inventory transfers between warehouses. Track pending, completed, and cancelled transfers.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <Link
            href="/stock-transfers/new"
            className="inline-flex items-center justify-center rounded-xl border border-transparent bg-gradient-to-r from-purple-500 to-pink-600 px-6 py-3 text-sm font-medium text-white shadow-sm hover:from-purple-600 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Transfer
          </Link>
        </div>
      </div>

      {/* Search */}
      <div className="mt-6">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-3 text-gray-900 border border-gray-300 rounded-xl bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
              placeholder="Search transfers by product, warehouse, or reference..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button
            type="submit"
            className="inline-flex items-center px-6 py-3 border border-transparent text-sm font-medium rounded-xl text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-all duration-200"
          >
            Search
          </button>
        </form>
      </div>

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="bg-white overflow-hidden shadow-sm rounded-xl border border-gray-200">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-6 w-6 text-yellow-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Pending Transfers</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {transfers.filter(t => t.status === 'pending').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-xl border border-gray-200">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-6 w-6 text-green-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Completed Transfers</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {transfers.filter(t => t.status === 'completed').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-xl border border-gray-200">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowRightLeft className="h-6 w-6 text-purple-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Transfers</dt>
                  <dd className="text-lg font-medium text-gray-900">{total}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Transfers Table */}
      <div className="mt-8 bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">
        {transfers.length === 0 ? (
          <div className="text-center py-12">
            <ArrowRightLeft className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No stock transfers</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating a new stock transfer.
            </p>
            <div className="mt-6">
              <Link
                href="/stock-transfers/new"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create Transfer
              </Link>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product & Reference
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Transfer Route
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quantity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Creator
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {transfers.map((transfer) => (
                  <tr key={transfer.id} className="hover:bg-gray-50 transition-colors duration-150">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {transfer.product?.name || `Product ID: ${transfer.product_id}`}
                        </div>
                        {transfer.transfer_reference && (
                          <div className="text-sm text-gray-500">
                            Ref: {transfer.transfer_reference}
                          </div>
                        )}
                        <div className="text-xs text-gray-400">
                          SKU: {transfer.product?.sku || 'N/A'}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <div className="text-sm text-gray-900">
                          {transfer.from_warehouse?.name || `Warehouse ${transfer.from_warehouse_id}`}
                        </div>
                        <ArrowRight className="h-4 w-4 text-gray-400" />
                        <div className="text-sm text-gray-900">
                          {transfer.to_warehouse?.name || `Warehouse ${transfer.to_warehouse_id}`}
                        </div>
                      </div>
                      {(transfer.from_warehouse?.location || transfer.to_warehouse?.location) && (
                        <div className="text-xs text-gray-500 mt-1">
                          {transfer.from_warehouse?.location} → {transfer.to_warehouse?.location}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {transfer.quantity}
                      </div>
                      <div className="text-xs text-gray-500">
                        {transfer.product?.unit_of_measure || 'units'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={getStatusBadge(transfer.status)}>
                        <span className="flex items-center">
                          {getStatusIcon(transfer.status)}
                          <span className="ml-1 capitalize">{transfer.status}</span>
                        </span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>{format(new Date(transfer.created_at), 'MMM dd, yyyy')}</div>
                      <div className="text-xs">{format(new Date(transfer.created_at), 'HH:mm')}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {canEditTransfer(transfer) ? (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                          You
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                          Other User
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {transfer.status === 'pending' && (
                        <div className="flex space-x-2">
                          {canEditTransfer(transfer) ? (
                            <>
                              <button
                                onClick={() => handleCompleteTransfer(transfer.id)}
                                className="text-green-600 hover:text-green-700 transition-colors duration-150"
                                title="Complete Transfer"
                              >
                                <CheckCircle className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => handleCancelTransfer(transfer.id)}
                                className="text-red-600 hover:text-red-700 transition-colors duration-150"
                                title="Cancel Transfer"
                              >
                                <XCircle className="h-4 w-4" />
                              </button>
                            </>
                          ) : (
                            <>
                              <span className="text-gray-300 cursor-not-allowed" title="You can only complete your own transfers">
                                <CheckCircle className="h-4 w-4" />
                              </span>
                              <span className="text-gray-300 cursor-not-allowed" title="You can only cancel your own transfers">
                                <XCircle className="h-4 w-4" />
                              </span>
                            </>
                          )}
                        </div>
                      )}
                      {transfer.status === 'completed' && transfer.completed_at && (
                        <div className="text-xs text-gray-500">
                          Completed: {format(new Date(transfer.completed_at), 'MMM dd, HH:mm')}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-between">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setPage(page - 1)}
              disabled={page === 1}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={page === totalPages}
              className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Showing page <span className="font-medium">{page}</span> of{' '}
                <span className="font-medium">{totalPages}</span>
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page === totalPages}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}