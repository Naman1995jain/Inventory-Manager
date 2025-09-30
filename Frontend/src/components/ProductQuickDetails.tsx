'use client';

import React, { useState } from 'react';
import { Product } from '@/types';
import { Eye, Info } from 'lucide-react';
import ProductDetailModal from './ProductDetailModal';

interface ProductQuickDetailsProps {
  products: Product[];
  title?: string;
  maxItems?: number;
}

export default function ProductQuickDetails({ 
  products, 
  title = "Products — Quick Details",
  maxItems = 4 
}: ProductQuickDetailsProps) {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const displayedProducts = products.slice(0, maxItems);

  const openModal = (product: Product) => {
    setSelectedProduct(product);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setSelectedProduct(null);
    setIsModalOpen(false);
  };

  return (
    <>
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          {products.length > maxItems && (
            <span className="text-sm text-gray-500">
              Showing {maxItems} of {products.length} products
            </span>
          )}
        </div>
        
        <div className="w-full">
          {displayedProducts.length === 0 ? (
            <div className="text-sm text-gray-500 text-center py-4">
              No product data to show
            </div>
          ) : (
            <div className="space-y-3">
              {displayedProducts.map((product) => (
                <div key={product.id} className="flex items-center justify-between border-b border-gray-100 pb-3 last:border-b-0 hover:bg-gray-50 p-2 rounded transition-colors">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900 truncate">
                          {product.name}
                        </div>
                        <div className="text-xs text-gray-500 flex items-center space-x-2">
                          <span>SKU: {product.sku || 'N/A'}</span>
                          <span>•</span>
                          <span>Stock: {product.total_stock || 0}</span>
                          <span>•</span>
                          <span>Price: {product.unit_price ? `$${product.unit_price}` : 'N/A'}</span>
                        </div>
                      </div>
                      <div className="ml-4 flex items-center space-x-2">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          (product.total_stock || 0) > 10 
                            ? 'bg-green-100 text-green-800'
                            : (product.total_stock || 0) > 0
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                        }`}>
                          {product.total_stock || 0}
                        </span>
                        <button
                          onClick={() => openModal(product)}
                          className="inline-flex items-center px-2 py-1 text-xs font-medium text-indigo-600 bg-indigo-50 rounded hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                          title="View full details"
                        >
                          <Info className="h-3 w-3 mr-1" />
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
        
        {products.length > maxItems && (
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-500">
              {products.length - maxItems} more products available. Visit the{' '}
              <a href="/products" className="text-indigo-600 hover:text-indigo-500 font-medium">
                Products page
              </a>{' '}
              to see all.
            </p>
          </div>
        )}
      </div>

      {/* Modal */}
      {selectedProduct && (
        <ProductDetailModal
          product={selectedProduct}
          isOpen={isModalOpen}
          onClose={closeModal}
        />
      )}
    </>
  );
}