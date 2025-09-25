'use client';

import React, { useState, useEffect } from 'react';
import { Product, ProductListResponse } from '@/types';
import { productService } from '@/lib/services';
import { useAuth } from '@/context/AuthContext';
import { Search, Plus, Edit, Trash2, Eye } from 'lucide-react';
import Link from 'next/link';
import toast from 'react-hot-toast';

export default function ProductList() {
  const { user } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  // Helper function to check if current user can edit this product
  const canEditProduct = (product: Product) => {
    // Admin can edit any product, regular users can only edit their own
    return user && (user.is_admin || product.created_by === user.id);
  };

  const fetchProducts = async () => {
    try {
      setIsLoading(true);
      const response: ProductListResponse = await productService.getProducts({
        page,
        page_size: 20,
        search: search || undefined,
        sort_by: 'created_desc'
      });
      
      setProducts(response.items);
      setTotalPages(response.total_pages);
      setTotal(response.total);
    } catch (error) {
      toast.error('Failed to fetch products');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [page, search]);

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await productService.deleteProduct(id);
        toast.success('Product deleted successfully');
        fetchProducts();
      } catch (error) {
        toast.error('Failed to delete product');
      }
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchProducts();
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Products</h1>
          <p className="mt-2 text-sm text-gray-700">
            A list of all products in your inventory with their current stock levels.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <Link
            href="/products/new"
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Product
          </Link>
        </div>
      </div>

      {/* Search */}
      <div className="mt-6">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="Search products..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>
          <button
            type="submit"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Search
          </button>
        </form>
      </div>

      {/* Products Table for md+ and Card list for small screens */}
      <div className="mt-8 flex flex-col">
        {/* Mobile: card list */}
        <div className="space-y-4 md:hidden">
          {isLoading ? (
            <div className="bg-white px-6 py-20 rounded-lg shadow">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                <p className="mt-2 text-sm text-gray-500">Loading products...</p>
              </div>
            </div>
          ) : (
            products.map((product) => (
              <div key={product.id} className="bg-white shadow rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 truncate">{product.name}</div>
                    <div className="mt-1 text-sm text-gray-500 truncate">{product.description || 'No description'}</div>
                    <div className="mt-2 flex items-center text-sm text-gray-500 space-x-3">
                      <div>SKU: <span className="text-gray-700">{product.sku}</span></div>
                      <div>Price: <span className="text-gray-700">{product.unit_price ? `$${product.unit_price}` : '-'}</span></div>
                    </div>
                  </div>
                  <div className="ml-4 flex-shrink-0 flex flex-col items-end space-y-2">
                    <div>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        (product.total_stock || 0) > 10 
                          ? 'bg-green-100 text-green-800'
                          : (product.total_stock || 0) > 0
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {product.total_stock || 0}
                      </span>
                    </div>
                    <div className="flex space-x-2">
                      <Link href={`/products/${product.id}`} className="text-indigo-600 hover:text-indigo-900">View</Link>
                      {canEditProduct(product) && (
                        <Link href={`/products/${product.id}/edit`} className="text-indigo-600 hover:text-indigo-900">Edit</Link>
                      )}
                      {!canEditProduct(product) && (
                        <span className="text-gray-400 cursor-not-allowed">Edit</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
        <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              {isLoading ? (
                <div className="bg-white px-6 py-20">
                  <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                    <p className="mt-2 text-sm text-gray-500">Loading products...</p>
                  </div>
                </div>
              ) : (
                <table className="min-w-full divide-y divide-gray-300 hidden md:table">
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
                        Price
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Stock
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Owner
                      </th>
                      <th className="relative px-6 py-3">
                        <span className="sr-only">Actions</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {products.map((product) => (
                      <tr key={product.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {product.name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {product.description || 'No description'}
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
                          {product.unit_price ? `$${product.unit_price}` : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            (product.total_stock || 0) > 10 
                              ? 'bg-green-100 text-green-800'
                              : (product.total_stock || 0) > 0
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {product.total_stock || 0}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            product.is_active 
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {product.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {canEditProduct(product) ? (
                            <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                              You
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                              Other User
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex space-x-2">
                            <Link
                              href={`/products/${product.id}`}
                              className="text-indigo-600 hover:text-indigo-900"
                              title="View Product"
                            >
                              <Eye className="h-4 w-4" />
                            </Link>
                            {canEditProduct(product) ? (
                              <>
                                <Link
                                  href={`/products/${product.id}/edit`}
                                  className="text-indigo-600 hover:text-indigo-900"
                                  title="Edit Product"
                                >
                                  <Edit className="h-4 w-4" />
                                </Link>
                                <button
                                  onClick={() => handleDelete(product.id)}
                                  className="text-red-600 hover:text-red-900"
                                  title="Delete Product"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </>
                            ) : (
                              <>
                                <span className="text-gray-300 cursor-not-allowed" title="You can only edit your own products">
                                  <Edit className="h-4 w-4" />
                                </span>
                                <span className="text-gray-300 cursor-not-allowed" title="You can only delete your own products">
                                  <Trash2 className="h-4 w-4" />
                                </span>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-6">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Showing <span className="font-medium">{(page - 1) * 20 + 1}</span> to{' '}
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
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
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