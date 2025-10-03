'use client';

import React, { useState, useEffect } from 'react';
import { StockMovement, StockMovementListResponse, MovementType } from '@/types';
import { stockMovementService } from '@/lib/services';
import { useAuth } from '@/context/AuthContext';
import { Search, Plus, TrendingUp, TrendingDown } from 'lucide-react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

export default function StockMovementList() {
  const { user } = useAuth();
  const [movements, setMovements] = useState<StockMovement[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  // Helper function to check if current user can edit this movement
  const canEditMovement = (movement: StockMovement) => {
    return user && movement.created_by === user.id;
  };

  const fetchMovements = async () => {
    try {
      setIsLoading(true);
      const response: StockMovementListResponse = await stockMovementService.getStockMovements({
        page,
        page_size: 20,
        search: search || undefined,
        sort_by: 'created_desc'
      });
      
      setMovements(response.items);
      setTotalPages(response.total_pages);
      setTotal(response.total);
    } catch (error) {
      toast.error('Failed to fetch stock movements');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMovements();
  }, [page, search]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchMovements();
  };

  const getMovementIcon = (type: MovementType) => {
    const inboundTypes = [MovementType.PURCHASE, MovementType.RETURN, MovementType.TRANSFER_IN];
    const isInbound = inboundTypes.includes(type);
    
    return isInbound ? (
      <TrendingUp className="h-4 w-4 text-green-500" />
    ) : (
      <TrendingDown className="h-4 w-4 text-red-500" />
    );
  };

  const getMovementTypeColor = (type: MovementType) => {
    switch (type) {
      case MovementType.PURCHASE:
        return 'bg-green-100 text-green-800';
      case MovementType.SALE:
        return 'bg-blue-100 text-blue-800';
      case MovementType.ADJUSTMENT:
        return 'bg-yellow-100 text-yellow-800';
      case MovementType.DAMAGED:
        return 'bg-red-100 text-red-800';
      case MovementType.RETURN:
        return 'bg-purple-100 text-purple-800';
      case MovementType.TRANSFER_IN:
        return 'bg-indigo-100 text-indigo-800';
      case MovementType.TRANSFER_OUT:
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">Stock Movements</h1>
          <p className="mt-1 text-sm text-gray-600">
            Track all inventory movements including purchases, sales, adjustments, and transfers.
          </p>
        </div>
        <Link
          href="/stock-movements/new"
          className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200"
        >
          <Plus className="h-4 w-4 mr-2" />
          Record Movement
        </Link>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <form onSubmit={handleSearch} className="flex flex-col gap-3 sm:flex-row sm:gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                placeholder="Search movements by product or reference..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>
          <button
            type="submit"
            className="inline-flex items-center justify-center px-4 py-2.5 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
          >
            Search
          </button>
        </form>
      </div>

      {/* Mobile Cards */}
      <div className="space-y-4 md:hidden">
        {isLoading ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-200 border-t-blue-600"></div>
              <p className="mt-3 text-sm text-gray-600">Loading movements...</p>
            </div>
          </div>
        ) : movements.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <div className="text-center">
              <TrendingUp className="mx-auto h-12 w-12 text-gray-300" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No movements found</h3>
              <p className="mt-1 text-sm text-gray-500">Get started by recording your first stock movement.</p>
              <div className="mt-6">
                <Link
                  href="/stock-movements/new"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Record Movement
                </Link>
              </div>
            </div>
          </div>
        ) : (
          movements.map((movement) => (
            <div key={movement.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow duration-200">
              {/* Movement Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    {getMovementIcon(movement.movement_type)}
                    <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${getMovementTypeColor(movement.movement_type)}`}>
                      {movement.movement_type.replace('_', ' ')}
                    </span>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 truncate">
                    {movement.product?.name || 'Unknown Product'}
                  </h3>
                  <p className="text-sm text-gray-500">{movement.product?.sku}</p>
                </div>
                <div className="ml-3 flex-shrink-0 text-right">
                  <div className={`text-lg font-bold ${movement.quantity > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {movement.quantity > 0 ? '+' : ''}{movement.quantity}
                  </div>
                  <div className="text-xs text-gray-500">
                    {format(new Date(movement.created_at), 'MMM dd, yyyy')}
                  </div>
                </div>
              </div>

              {/* Movement Details */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div>
                  <p className="text-xs font-medium text-gray-500">Total Cost</p>
                  <p className="text-sm text-gray-900">{movement.total_cost ? `$${movement.total_cost}` : '-'}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-500">Reference</p>
                  <p className="text-sm text-gray-900">{movement.reference_number || '-'}</p>
                </div>
              </div>

              {/* Creator Info */}
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-xs font-medium text-gray-500">Created By</p>
                  <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${
                    canEditMovement(movement) ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {movement.creator?.email || 'Unknown'}
                  </span>
                </div>
              </div>

              {/* Notes */}
              {movement.notes && (
                <div className="border-t border-gray-200 pt-3">
                  <p className="text-xs font-medium text-gray-500 mb-1">Notes</p>
                  <p className="text-sm text-gray-700">{movement.notes}</p>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Desktop Table */}
      <div className="hidden md:block bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {isLoading ? (
          <div className="px-6 py-20">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-200 border-t-blue-600"></div>
              <p className="mt-3 text-sm text-gray-600">Loading movements...</p>
            </div>
          </div>
        ) : movements.length === 0 ? (
          <div className="px-6 py-20">
            <div className="text-center">
              <TrendingUp className="mx-auto h-12 w-12 text-gray-300" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No movements found</h3>
              <p className="mt-1 text-sm text-gray-500">Get started by recording your first stock movement.</p>
            </div>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cost
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Reference
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Creator
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Notes
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {movements.map((movement) => (
                <tr key={movement.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {format(new Date(movement.created_at), 'MMM dd, yyyy')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {movement.product?.name || 'Unknown Product'}
                      </div>
                      <div className="text-sm text-gray-500">
                        {movement.product?.sku}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getMovementIcon(movement.movement_type)}
                      <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getMovementTypeColor(movement.movement_type)}`}>
                        {movement.movement_type.replace('_', ' ')}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <span className={movement.quantity > 0 ? 'text-green-600' : 'text-red-600'}>
                      {movement.quantity > 0 ? '+' : ''}{movement.quantity}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {movement.total_cost ? `$${movement.total_cost}` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {movement.reference_number || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {movement.creator?.email ? (
                      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium ${
                        canEditMovement(movement) ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                      } rounded-full`}>
                        {movement.creator.email}
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                        Unknown
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {movement.notes || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 px-4 py-3 flex items-center justify-between sm:px-6">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              Previous
            </button>
            <span className="text-sm text-gray-700 flex items-center">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Showing <span className="font-medium">{(page - 1) * 1 + 1}</span> to{' '}
                <span className="font-medium">
                  {Math.min(page * 20, total)}
                </span>{' '}
                of <span className="font-medium">{total}</span> results
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
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