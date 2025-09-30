'use client';

import React, { useState } from 'react';
import { StockMovement } from '@/types';
import { X, TrendingUp, TrendingDown, Eye, Calendar, MapPin, Package, DollarSign, User } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import ProductDetailModal from './ProductDetailModal';

interface TransactionsModalProps {
  transactions: StockMovement[];
  isOpen: boolean;
  onClose: () => void;
}

export default function TransactionsModal({ transactions, isOpen, onClose }: TransactionsModalProps) {
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [isProductModalOpen, setIsProductModalOpen] = useState(false);

  if (!isOpen) return null;

  const openProductModal = (transaction: StockMovement) => {
    // Create a product object from transaction data
    const product = {
      id: transaction.product_id,
      name: transaction.product_name || `Product ${transaction.product_id}`,
      sku: '',
      description: transaction.notes || '',
      unit_price: transaction.unit_cost,
      unit_of_measure: 'units',
      category: '',
      is_active: true,
      created_at: transaction.created_at,
      updated_at: transaction.created_at,
      created_by: transaction.created_by,
      total_stock: 0,
      creator: transaction.creator
    };
    setSelectedProduct(product);
    setIsProductModalOpen(true);
  };

  const closeProductModal = () => {
    setSelectedProduct(null);
    setIsProductModalOpen(false);
  };

  return (
    <>
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div className="flex min-h-screen items-center justify-center p-2 sm:p-4">
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
            onClick={onClose}
          />
          
          {/* Modal */}
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[85vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between p-3 sm:p-6 border-b border-gray-200">
              <div className="flex items-center space-x-2 sm:space-x-3">
                <Package className="h-5 w-5 sm:h-6 sm:w-6 text-indigo-600" />
                <h2 className="text-lg sm:text-xl font-semibold text-gray-900">All Recent Transactions</h2>
                <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs sm:text-sm">
                  {transactions.length}
                </span>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* Content */}
            <div className="p-3 sm:p-6">
              {transactions.length === 0 ? (
                <div className="text-center py-12">
                  <Package className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-500">No transactions found</p>
                </div>
              ) : (
                <div className="space-y-3 sm:space-y-4">
                  {transactions.map((transaction, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-3 sm:p-4 hover:bg-gray-50 transition-colors">
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
                              <h3 className="text-sm font-semibold text-gray-900">
                                {transaction.product?.name || transaction.product_name || `Product ${transaction.product_id}`}
                              </h3>
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                transaction.movement_type === 'purchase'
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-red-100 text-red-800'
                              }`}>
                                {transaction.movement_type.toUpperCase()}
                              </span>
                            </div>
                            
                            {/* Product Details */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-gray-600 mb-3">
                              <div className="flex items-center space-x-1">
                                <Package className="h-3 w-3" />
                                <span className="font-medium">SKU:</span>
                                <span>{transaction.product?.sku || 'N/A'}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Package className="h-3 w-3" />
                                <span className="font-medium">Category:</span>
                                <span>{transaction.product?.category || 'N/A'}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Package className="h-3 w-3" />
                                <span className="font-medium">Unit:</span>
                                <span>{transaction.product?.unit_of_measure || 'units'}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Calendar className="h-3 w-3" />
                                <span className="font-medium">Date:</span>
                                <span>{format(parseISO(transaction.created_at), 'MMM dd, yyyy HH:mm')}</span>
                              </div>
                            </div>

                            {/* Warehouse Details */}
                            <div className="mb-3">
                              <div className="flex items-center space-x-1 text-xs text-gray-600 mb-1">
                                <MapPin className="h-3 w-3" />
                                <span className="font-medium">Warehouse:</span>
                                <span>{transaction.warehouse?.name || transaction.warehouse_name || `Warehouse ${transaction.warehouse_id}`}</span>
                              </div>
                              {transaction.warehouse?.location && (
                                <div className="text-xs text-gray-500 ml-4">
                                  Location: {transaction.warehouse.location}
                                </div>
                              )}
                              {transaction.warehouse?.description && (
                                <div className="text-xs text-gray-500 ml-4">
                                  {transaction.warehouse.description}
                                </div>
                              )}
                            </div>

                            {/* Transaction Details */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-gray-600 mb-3">
                              <div className="flex items-center space-x-1">
                                <Package className="h-3 w-3" />
                                <span className="font-medium">Quantity:</span>
                                <span>{Math.abs(transaction.quantity)} {transaction.product?.unit_of_measure || 'units'}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <DollarSign className="h-3 w-3" />
                                <span className="font-medium">Unit Cost:</span>
                                <span>${transaction.unit_cost ? parseFloat(transaction.unit_cost).toFixed(2) : 'N/A'}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <DollarSign className="h-3 w-3" />
                                <span className="font-medium">Total Cost:</span>
                                <span>${Math.abs(transaction.total_cost || 0).toLocaleString()}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <User className="h-3 w-3" />
                                <span className="font-medium">Created by:</span>
                                <span>{transaction.creator?.email || 'Unknown'}</span>
                              </div>
                            </div>

                            {/* Reference Number */}
                            {transaction.reference_number && (
                              <div className="mb-2 text-xs text-gray-600">
                                <span className="font-medium">Reference:</span> {transaction.reference_number}
                              </div>
                            )}

                            {/* Product Description */}
                            {transaction.product?.description && (
                              <div className="mb-2 text-xs text-gray-600 bg-blue-50 p-2 rounded">
                                <span className="font-medium">Product Description:</span> {transaction.product.description}
                              </div>
                            )}

                            {/* Notes */}
                            {transaction.notes && (
                              <div className="text-xs text-gray-600 bg-gray-100 p-2 rounded">
                                <span className="font-medium">Notes:</span> {transaction.notes}
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center space-x-4 ml-4">
                          <div className="text-right">
                            <div className={`text-lg font-semibold ${
                              transaction.movement_type === 'purchase' ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {transaction.movement_type === 'purchase' ? '+' : '-'}{Math.abs(transaction.quantity)}
                            </div>
                            <div className="text-sm text-gray-500 flex items-center">
                              <DollarSign className="h-3 w-3 mr-1" />
                              {Math.abs(transaction.total_cost || 0).toLocaleString()}
                            </div>
                            {transaction.unit_cost && (
                              <div className="text-xs text-gray-400">
                                ${transaction.unit_cost}/unit
                              </div>
                            )}
                          </div>
                          
                          <button
                            onClick={() => openProductModal(transaction)}
                            className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-indigo-600 bg-indigo-50 rounded-md hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                            title="View product details"
                          >
                            <Eye className="h-3 w-3 mr-1" />
                            Details
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
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

      {/* Product Detail Modal */}
      {selectedProduct && (
        <ProductDetailModal
          product={selectedProduct}
          isOpen={isProductModalOpen}
          onClose={closeProductModal}
        />
      )}
    </>
  );
}