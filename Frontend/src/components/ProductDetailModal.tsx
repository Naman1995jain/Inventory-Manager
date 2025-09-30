'use client';

import React from 'react';
import { Product, ProductWithStock } from '@/types';
import { X, Package, DollarSign, Tag, FileText, Ruler, Calendar, User, Eye } from 'lucide-react';
import { format } from 'date-fns';

interface ProductDetailModalProps {
  product: Product | ProductWithStock;
  isOpen: boolean;
  onClose: () => void;
}

export default function ProductDetailModal({ product, isOpen, onClose }: ProductDetailModalProps) {
  if (!isOpen) return null;

  const isProductWithStock = (prod: Product | ProductWithStock): prod is ProductWithStock => {
    return 'warehouse_stock' in prod;
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-2 sm:p-4">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
        />
        
        {/* Modal */}
        <div className="relative bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-3 sm:p-6 border-b border-gray-200">
            <div className="flex items-center space-x-2 sm:space-x-3">
              <Package className="h-5 w-5 sm:h-6 sm:w-6 text-indigo-600" />
              <h2 className="text-lg sm:text-xl font-semibold text-gray-900">Product Details</h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-5 w-5 sm:h-6 sm:w-6" />
            </button>
          </div>

          {/* Content */}
          <div className="p-3 sm:p-6 space-y-4 sm:space-y-6">
            {/* Basic Information */}
            <div>
              <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-3 sm:mb-4">Basic Information</h3>
              <div className="grid grid-cols-1 gap-3 sm:gap-4">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Package className="inline h-4 w-4 mr-1" />
                      Product Name
                    </label>
                    <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">{product.name}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Tag className="inline h-4 w-4 mr-1" />
                      SKU
                    </label>
                    <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">{product.sku || 'N/A'}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Tag className="inline h-4 w-4 mr-1" />
                      Category
                    </label>
                    <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">{product.category || 'Uncategorized'}</p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <DollarSign className="inline h-4 w-4 mr-1" />
                      Unit Price
                    </label>
                    <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">
                      {product.unit_price ? `$${product.unit_price}` : 'Not set'}
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Ruler className="inline h-4 w-4 mr-1" />
                      Unit of Measure
                    </label>
                    <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">{product.unit_of_measure || 'units'}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Package className="inline h-4 w-4 mr-1" />
                      Total Stock
                    </label>
                    <p className={`text-sm font-semibold p-2 rounded ${
                      (product.total_stock || 0) > 10 
                        ? 'bg-green-50 text-green-800'
                        : (product.total_stock || 0) > 0
                          ? 'bg-yellow-50 text-yellow-800'
                          : 'bg-red-50 text-red-800'
                    }`}>
                      {product.total_stock || 0} {product.unit_of_measure || 'units'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Description */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Description</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <FileText className="inline h-4 w-4 mr-1" />
                  Product Description
                </label>
                <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded min-h-[60px]">
                  {product.description || 'No description available'}
                </p>
              </div>
            </div>

            {/* Stock Distribution (if ProductWithStock) */}
            {isProductWithStock(product) && product.warehouse_stock && product.warehouse_stock.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Stock Distribution</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="space-y-2">
                    {product.warehouse_stock.map((stock) => (
                      <div key={stock.warehouse_id} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                        <span className="text-sm font-medium text-gray-700">{stock.warehouse_name}</span>
                        <span className={`text-sm font-semibold ${
                          stock.current_stock > 10 
                            ? 'text-green-600'
                            : stock.current_stock > 0
                              ? 'text-yellow-600'
                              : 'text-red-600'
                        }`}>
                          {stock.current_stock} {product.unit_of_measure || 'units'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Meta Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Additional Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Calendar className="inline h-4 w-4 mr-1" />
                      Created Date
                    </label>
                    <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">
                      {format(new Date(product.created_at), 'PPP')}
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Calendar className="inline h-4 w-4 mr-1" />
                      Last Updated
                    </label>
                    <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">
                      {format(new Date(product.updated_at), 'PPP')}
                    </p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <User className="inline h-4 w-4 mr-1" />
                      Created By
                    </label>
                    <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">
                      {product.creator?.email || 'Unknown'}
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Eye className="inline h-4 w-4 mr-1" />
                      Status
                    </label>
                    <p className={`text-sm font-medium p-2 rounded ${
                      product.is_active 
                        ? 'bg-green-50 text-green-800'
                        : 'bg-red-50 text-red-800'
                    }`}>
                      {product.is_active ? 'Active' : 'Inactive'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-3 px-6 py-4 bg-gray-50 border-t border-gray-200">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}