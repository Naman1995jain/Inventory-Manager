'use client';

import React, { useState, useEffect } from 'react';
import { StockTransferCreate, Product, Warehouse } from '@/types';
import { stockTransferService, productService, warehouseService } from '@/lib/services';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { ArrowLeft, Save, Package, Warehouse as WarehouseIcon, ArrowRightLeft, FileText, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function StockTransferForm() {
  const [formData, setFormData] = useState<StockTransferCreate>({
    product_id: 0,
    from_warehouse_id: 0,
    to_warehouse_id: 0,
    quantity: 0,
    transfer_reference: '',
    notes: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [productsResponse, warehousesResponse] = await Promise.all([
          productService.getProducts({ page: 1, page_size: 20 }),
          warehouseService.getWarehouses()
        ]);
        setProducts(productsResponse.items);
        setWarehouses(warehousesResponse);
      } catch (error) {
        toast.error('Failed to load form data');
      } finally {
        setLoadingData(false);
      }
    };

    fetchData();
  }, []);

  // Validation function
  const validateField = (name: string, value: any): string => {
    switch (name) {
      case 'product_id':
        if (!value || value === 0) {
          return 'Please select a product';
        }
        return '';
      case 'from_warehouse_id':
        if (!value || value === 0) {
          return 'Please select source warehouse';
        }
        return '';
      case 'to_warehouse_id':
        if (!value || value === 0) {
          return 'Please select destination warehouse';
        }
        if (value === formData.from_warehouse_id) {
          return 'Destination warehouse must be different from source';
        }
        return '';
      case 'quantity':
        if (!value || value <= 0) {
          return 'Quantity must be greater than 0';
        }
        return '';
      default:
        return '';
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    let processedValue: any = value;

    if (name === 'product_id' || name === 'from_warehouse_id' || name === 'to_warehouse_id') {
      processedValue = parseInt(value);
    } else if (name === 'quantity') {
      processedValue = parseInt(value);
    }
    
    setFormData(prev => ({
      ...prev,
      [name]: processedValue
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }

    // Also validate the other warehouse field if this is a warehouse change
    if (name === 'from_warehouse_id' || name === 'to_warehouse_id') {
      const otherField = name === 'from_warehouse_id' ? 'to_warehouse_id' : 'from_warehouse_id';
      const otherValue = name === 'from_warehouse_id' ? formData.to_warehouse_id : formData.from_warehouse_id;
      
      if (otherValue && processedValue === otherValue) {
        setErrors(prev => ({
          ...prev,
          [name]: 'Warehouses must be different',
          [otherField]: 'Warehouses must be different'
        }));
      } else {
        setErrors(prev => ({
          ...prev,
          [name]: '',
          [otherField]: ''
        }));
      }
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
    
    const error = validateField(name, name === 'product_id' || name === 'from_warehouse_id' || name === 'to_warehouse_id' ? parseInt(value) : value);
    setErrors(prev => ({
      ...prev,
      [name]: error
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Validate all fields
    const newErrors: Record<string, string> = {};
    Object.entries(formData).forEach(([key, value]) => {
      const error = validateField(key, value);
      if (error) newErrors[key] = error;
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setTouched(Object.keys(formData).reduce((acc, key) => ({ ...acc, [key]: true }), {}));
      setIsLoading(false);
      return;
    }

    try {
      await stockTransferService.createStockTransfer(formData);
      toast.success('Stock transfer created successfully!');
      router.push('/stock-transfers');
    } catch (error) {
      console.error('Error creating stock transfer:', error);
      toast.error('Failed to create stock transfer. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const selectedFromWarehouse = warehouses.find(w => w.id === formData.from_warehouse_id);
  const selectedToWarehouse = warehouses.find(w => w.id === formData.to_warehouse_id);

  if (loadingData) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="bg-white p-8 rounded-2xl space-y-6">
              <div className="h-6 bg-gray-200 rounded"></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="h-12 bg-gray-200 rounded"></div>
                <div className="h-12 bg-gray-200 rounded"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/stock-transfers"
            className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors duration-200"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Stock Transfers
          </Link>
          <div className="mt-4">
            <h1 className="text-3xl font-bold text-gray-900">Create Stock Transfer</h1>
            <p className="mt-2 text-sm text-gray-600">
              Transfer inventory between warehouses. Transfers are created in pending status and need to be completed manually.
            </p>
          </div>
        </div>

        {/* Form Container */}
        <div className="bg-white shadow-xl rounded-2xl overflow-hidden">
          {/* Form Header */}
          <div className="bg-gradient-to-r from-purple-500 to-pink-600 px-6 py-4">
            <div className="flex items-center">
              <ArrowRightLeft className="h-6 w-6 text-white mr-3" />
              <h2 className="text-xl font-semibold text-white">Transfer Details</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="p-8 space-y-8">
            {/* Product Selection */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <Package className="h-5 w-5 mr-2 text-purple-500" />
                Product Selection
              </h3>
              <div className="space-y-1">
                <label htmlFor="product_id" className="block text-sm font-semibold text-gray-700">
                  Product <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <select
                    name="product_id"
                    id="product_id"
                    required
                    className={`block w-full px-4 py-3 text-gray-900 border-2 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent appearance-none bg-white ${
                      errors.product_id && touched.product_id
                        ? 'border-red-300 bg-red-50 focus:ring-red-500'
                        : 'border-gray-200 hover:border-gray-300 focus:border-purple-500'
                    }`}
                    value={formData.product_id}
                    onChange={handleChange}
                    onBlur={handleBlur}
                  >
                    <option value={0}>Select a product...</option>
                    {products.map((product) => (
                      <option key={product.id} value={product.id}>
                        {product.name} ({product.sku})
                      </option>
                    ))}
                  </select>
                  <Package className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
                </div>
                {errors.product_id && touched.product_id && (
                  <p className="text-sm text-red-600 flex items-center mt-1">
                    <span className="w-1 h-1 bg-red-600 rounded-full mr-2"></span>
                    {errors.product_id}
                  </p>
                )}
              </div>
            </div>

            {/* Warehouse Transfer Route */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <WarehouseIcon className="h-5 w-5 mr-2 text-purple-500" />
                Transfer Route
              </h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* From Warehouse */}
                <div className="space-y-1">
                  <label htmlFor="from_warehouse_id" className="block text-sm font-semibold text-gray-700">
                    From Warehouse <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <select
                      name="from_warehouse_id"
                      id="from_warehouse_id"
                      required
                      className={`block w-full px-4 py-3 text-gray-900 border-2 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent appearance-none bg-white ${
                        errors.from_warehouse_id && touched.from_warehouse_id
                          ? 'border-red-300 bg-red-50 focus:ring-red-500'
                          : 'border-gray-200 hover:border-gray-300 focus:border-purple-500'
                      }`}
                      value={formData.from_warehouse_id}
                      onChange={handleChange}
                      onBlur={handleBlur}
                    >
                      <option value={0}>Select source warehouse...</option>
                      {warehouses.map((warehouse) => (
                        <option key={warehouse.id} value={warehouse.id}>
                          {warehouse.name} - {warehouse.location}
                        </option>
                      ))}
                    </select>
                    <WarehouseIcon className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
                  </div>
                  {errors.from_warehouse_id && touched.from_warehouse_id && (
                    <p className="text-sm text-red-600 flex items-center mt-1">
                      <span className="w-1 h-1 bg-red-600 rounded-full mr-2"></span>
                      {errors.from_warehouse_id}
                    </p>
                  )}
                </div>

                {/* To Warehouse */}
                <div className="space-y-1">
                  <label htmlFor="to_warehouse_id" className="block text-sm font-semibold text-gray-700">
                    To Warehouse <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <select
                      name="to_warehouse_id"
                      id="to_warehouse_id"
                      required
                      className={`block w-full px-4 py-3 text-gray-900 border-2 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent appearance-none bg-white ${
                        errors.to_warehouse_id && touched.to_warehouse_id
                          ? 'border-red-300 bg-red-50 focus:ring-red-500'
                          : 'border-gray-200 hover:border-gray-300 focus:border-purple-500'
                      }`}
                      value={formData.to_warehouse_id}
                      onChange={handleChange}
                      onBlur={handleBlur}
                    >
                      <option value={0}>Select destination warehouse...</option>
                      {warehouses.map((warehouse) => (
                        <option 
                          key={warehouse.id} 
                          value={warehouse.id}
                          disabled={warehouse.id === formData.from_warehouse_id}
                        >
                          {warehouse.name} - {warehouse.location}
                        </option>
                      ))}
                    </select>
                    <WarehouseIcon className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
                  </div>
                  {errors.to_warehouse_id && touched.to_warehouse_id && (
                    <p className="text-sm text-red-600 flex items-center mt-1">
                      <span className="w-1 h-1 bg-red-600 rounded-full mr-2"></span>
                      {errors.to_warehouse_id}
                    </p>
                  )}
                </div>
              </div>

              {/* Transfer Route Visualization */}
              {selectedFromWarehouse && selectedToWarehouse && (
                <div className="mt-6 p-4 bg-purple-50 rounded-xl border border-purple-200">
                  <h4 className="text-sm font-medium text-purple-900 mb-3">Transfer Route</h4>
                  <div className="flex items-center justify-center space-x-4">
                    <div className="text-center">
                      <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-100 rounded-full border-2 border-purple-200">
                        <WarehouseIcon className="h-6 w-6 text-purple-600" />
                      </div>
                      <div className="mt-2">
                        <div className="text-sm font-medium text-purple-900">{selectedFromWarehouse.name}</div>
                        <div className="text-xs text-purple-600">{selectedFromWarehouse.location}</div>
                      </div>
                    </div>
                    
                    <div className="flex-1 flex items-center justify-center">
                      <ArrowRight className="h-8 w-8 text-purple-400" />
                    </div>
                    
                    <div className="text-center">
                      <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-100 rounded-full border-2 border-purple-200">
                        <WarehouseIcon className="h-6 w-6 text-purple-600" />
                      </div>
                      <div className="mt-2">
                        <div className="text-sm font-medium text-purple-900">{selectedToWarehouse.name}</div>
                        <div className="text-xs text-purple-600">{selectedToWarehouse.location}</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Quantity */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <ArrowRightLeft className="h-5 w-5 mr-2 text-purple-500" />
                Transfer Quantity
              </h3>
              <div className="max-w-xs space-y-1">
                <label htmlFor="quantity" className="block text-sm font-semibold text-gray-700">
                  Quantity <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  name="quantity"
                  id="quantity"
                  required
                  min="1"
                  className={`block w-full px-4 py-3 text-gray-900 border-2 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                    errors.quantity && touched.quantity
                      ? 'border-red-300 bg-red-50 focus:ring-red-500'
                      : 'border-gray-200 hover:border-gray-300 focus:border-purple-500'
                  }`}
                  placeholder="0"
                  value={formData.quantity || ''}
                  onChange={handleChange}
                  onBlur={handleBlur}
                />
                {errors.quantity && touched.quantity && (
                  <p className="text-sm text-red-600 flex items-center mt-1">
                    <span className="w-1 h-1 bg-red-600 rounded-full mr-2"></span>
                    {errors.quantity}
                  </p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Number of units to transfer
                </p>
              </div>
            </div>

            {/* Reference & Notes */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <FileText className="h-5 w-5 mr-2 text-purple-500" />
                Additional Information
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Transfer Reference */}
                <div className="space-y-1">
                  <label htmlFor="transfer_reference" className="block text-sm font-semibold text-gray-700">
                    Transfer Reference (Optional)
                  </label>
                  <input
                    type="text"
                    name="transfer_reference"
                    id="transfer_reference"
                    className="block w-full px-4 py-3 text-gray-900 border-2 border-gray-200 rounded-xl shadow-sm transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="e.g., TR-001, TRANSFER-123..."
                    value={formData.transfer_reference}
                    onChange={handleChange}
                    onBlur={handleBlur}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Internal reference number for this transfer
                  </p>
                </div>

                {/* Notes */}
                <div className="space-y-1">
                  <label htmlFor="notes" className="block text-sm font-semibold text-gray-700">
                    Notes (Optional)
                  </label>
                  <textarea
                    name="notes"
                    id="notes"
                    rows={3}
                    className="block w-full px-4 py-3 text-gray-900 border-2 border-gray-200 rounded-xl shadow-sm transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                    placeholder="Reason for transfer, special instructions..."
                    value={formData.notes}
                    onChange={handleChange}
                    onBlur={handleBlur}
                  />
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row justify-end space-y-3 sm:space-y-0 sm:space-x-4 pt-6 border-t border-gray-200">
              <Link
                href="/stock-transfers"
                className="inline-flex justify-center items-center px-6 py-3 border-2 border-gray-300 rounded-xl shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-all duration-200"
              >
                Cancel
              </Link>
              <button
                type="submit"
                disabled={isLoading}
                className="inline-flex justify-center items-center px-8 py-3 border-2 border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Creating Transfer...
                  </>
                ) : (
                  <>
                    <Save className="h-5 w-5 mr-2" />
                    Create Transfer
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}