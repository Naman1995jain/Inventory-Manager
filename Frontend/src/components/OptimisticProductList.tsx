'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Product, ProductListResponse } from '@/types';
import { productService } from '@/lib/services';
import { useAuth } from '@/context/AuthContext';
import { useInstantProductUpdates, useOptimisticUpdates } from '@/hooks/useInstantUpdates';
import { Search, Plus, Edit, Trash2, Eye } from 'lucide-react';
import Link from 'next/link';
import toast from 'react-hot-toast';

export default function OptimisticProductList() {
  const { user } = useAuth();
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  // Helper function to check if current user can edit this product
  const canEditProduct = (product: Product) => {
    return user && (user.is_admin || product.created_by === user.id);
  };

  const fetchProducts = useCallback(async () => {
    const response: ProductListResponse = await productService.getProducts({
      page,
      page_size: 20,
      search: search || undefined,
      sort_by: 'created_desc'
    });
    return response.items;
  }, [page, search]);

  // Use optimistic updates
  const {
    data: products,
    isLoading: optimisticLoading,
    addOptimistic,
    updateOptimistic,
    removeOptimistic,
    refresh
  } = useOptimisticUpdates([], fetchProducts, (product) => product.id);

  // Handle real-time updates from WebSocket
  const handleProductUpdate = useCallback((message: any) => {
    const { action, product, product_id } = message.data || message;
    
    switch (action) {
      case 'created':
        // Product already added optimistically, just confirm
        toast.success(`Product "${product.name}" created successfully!`);
        break;
        
      case 'updated':
        // Update the product in the list
        updateOptimistic(product);
        toast.success(`Product "${product.name}" updated!`);
        break;
        
      case 'deleted':
        // Remove the product from the list
        removeOptimistic(product_id);
        toast.success('Product deleted successfully!');
        break;
    }
  }, [updateOptimistic, removeOptimistic]);

  // Subscribe to instant product updates
  useInstantProductUpdates(handleProductUpdate);

  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        const response: ProductListResponse = await productService.getProducts({
          page,
          page_size: 20,
          search: search || undefined,
          sort_by: 'created_desc'
        });
        
        setTotalPages(response.total_pages);
        setTotal(response.total);
      } catch (error) {
        toast.error('Failed to fetch products');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
    refresh(); // Refresh optimistic data
  }, [page, search, refresh]);

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        // Optimistically remove from UI
        removeOptimistic(id);
        
        // Delete on server
        await productService.deleteProduct(id);
        
        // Success will be confirmed via WebSocket
        setTotal(prev => prev - 1);
      } catch (error) {
        // Refresh on error to restore state
        refresh();
        toast.error('Failed to delete product');
      }
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
    setPage(1); // Reset to first page on search
  };

  if (isLoading && !products.length) {
    return (
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
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
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Products</h1>
          <p className="mt-2 text-sm text-gray-700">
            A list of all products in your inventory including their stock levels and details.
            <span className="ml-2 text-xs text-green-600 font-medium">
              ⚡ Real-time updates enabled
            </span>
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <Link
            href="/products/create"
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Product
          </Link>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="mt-6">
        <div className="max-w-md">
          <div className="relative rounded-md shadow-sm">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={search}
              onChange={handleSearchChange}
              className="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md"
              placeholder="Search products..."
            />
          </div>
        </div>
      </div>

      {/* Products Table */}
      <div className="mt-8 flex flex-col">
        <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Product
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      SKU
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Category
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stock
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="relative px-6 py-3">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {products.map((product, index) => (
                    <tr 
                      key={product.id}
                      className={`hover:bg-gray-50 transition-colors duration-150 ${
                        index === 0 ? 'animate-pulse bg-green-50' : ''
                      }`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {product.name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {product.description}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {product.sku}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {product.category || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          (product.total_stock || 0) < 10 
                            ? 'bg-red-100 text-red-800' 
                            : (product.total_stock || 0) < 50 
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-green-100 text-green-800'
                        }`}>
                          {product.total_stock || 0} {product.unit_of_measure || 'units'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {product.unit_price ? `$${product.unit_price}` : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex space-x-2">
                          <Link
                            href={`/products/${product.id}`}
                            className="text-indigo-600 hover:text-indigo-900"
                            title="View details"
                          >
                            <Eye className="h-4 w-4" />
                          </Link>
                          {canEditProduct(product) && (
                            <>
                              <Link
                                href={`/products/${product.id}/edit`}
                                className="text-indigo-600 hover:text-indigo-900"
                                title="Edit product"
                              >
                                <Edit className="h-4 w-4" />
                              </Link>
                              <button
                                onClick={() => handleDelete(product.id)}
                                className="text-red-600 hover:text-red-900"
                                title="Delete product"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {products.length} of {total} products
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 text-sm bg-white border border-gray-300 rounded-md disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-3 py-1 text-sm">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-3 py-1 text-sm bg-white border border-gray-300 rounded-md disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Real-time indicator */}
      <div className="mt-4 text-center">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <span className="w-2 h-2 bg-green-400 rounded-full mr-1 animate-pulse"></span>
          Live updates active
        </span>
      </div>
    </div>
  );
}