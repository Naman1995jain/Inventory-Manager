'use client';

import React, { useState } from 'react';
import { Product } from '@/types';
import { Eye, TrendingUp, TrendingDown } from 'lucide-react';
import ProductDetailModal from './ProductDetailModal';

interface StockListSectionProps {
  products: Product[];
  title: string;
  type: 'low' | 'high';
  maxItems?: number;
}

interface StockListModalProps {
  products: Product[];
  title: string;
  type: 'low' | 'high';
  isOpen: boolean;
  onClose: () => void;
}

function StockListModal({ products, title, type, isOpen, onClose }: StockListModalProps) {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isProductModalOpen, setIsProductModalOpen] = useState(false);

  if (!isOpen) return null;

  const openProductModal = (product: Product) => {
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
        <div className="flex min-h-screen items-center justify-center p-4">
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
            onClick={onClose}
          />
          
          {/* Modal */}
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                {type === 'low' ? (
                  <TrendingDown className="h-6 w-6 text-red-600" />
                ) : (
                  <TrendingUp className="h-6 w-6 text-green-600" />
                )}
                <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              {products.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-500">No products to display</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {products.map((product) => (
                    <div key={product.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{product.name}</div>
                            <div className="text-xs text-gray-500 flex items-center space-x-2">
                              <span>SKU: {product.sku || 'N/A'}</span>
                              <span>•</span>
                              <span>Category: {product.category || 'Uncategorized'}</span>
                              {product.unit_price && (
                                <>
                                  <span>•</span>
                                  <span>Price: ${product.unit_price}</span>
                                </>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center space-x-3">
                            <span className={`text-sm font-semibold ${
                              type === 'low' ? 'text-red-600' : 'text-green-600'
                            }`}>
                              {product.total_stock || 0} {product.unit_of_measure || 'units'}
                            </span>
                            <button
                              onClick={() => openProductModal(product)}
                              className="inline-flex items-center px-2 py-1 text-xs font-medium text-indigo-600 bg-indigo-50 rounded hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                              title="View full details"
                            >
                              <Eye className="h-3 w-3 mr-1" />
                              Details
                            </button>
                          </div>
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

export default function StockListSection({ products, title, type, maxItems = 4 }: StockListSectionProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const displayedProducts = products.slice(0, maxItems);
  const hasMoreProducts = products.length > maxItems;

  const openModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <>
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          {hasMoreProducts && (
            <button
              onClick={openModal}
              className="text-sm text-indigo-600 hover:text-indigo-500 font-medium"
            >
              View All ({products.length})
            </button>
          )}
        </div>
        
        {displayedProducts.length === 0 ? (
          <div className="text-sm text-gray-500 text-center py-4">
            No products to display
          </div>
        ) : (
          <ul className="space-y-3">
            {displayedProducts.map((product) => (
              <li key={product.id} className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-gray-900">{product.name}</div>
                  <div className="text-xs text-gray-500">SKU: {product.sku || 'N/A'}</div>
                </div>
                <div className={`text-sm font-semibold ${
                  type === 'low' ? 'text-red-600' : 'text-green-600'
                }`}>
                  {product.total_stock || 0}
                </div>
              </li>
            ))}
          </ul>
        )}
        
        {hasMoreProducts && (
          <div className="mt-4 text-center">
            <button
              onClick={openModal}
              className="inline-flex items-center px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-md hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
            >
              View All {products.length} Products
            </button>
          </div>
        )}
      </div>

      {/* Stock List Modal */}
      <StockListModal
        products={products}
        title={title}
        type={type}
        isOpen={isModalOpen}
        onClose={closeModal}
      />
    </>
  );
}