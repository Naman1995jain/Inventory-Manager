'use client';

import React, { useState, useEffect } from 'react';
import { StockMovementCreate, MovementType, Product, Warehouse } from '@/types';
import { stockMovementService, productService, warehouseService } from '@/lib/services';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { ArrowLeft, Save, Package, Warehouse as WarehouseIcon, DollarSign, FileText, ArrowUpDown } from 'lucide-react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';

export default function StockMovementForm() {
  const [formData, setFormData] = useState<StockMovementCreate>({
    product_id: 0,
    warehouse_id: 0,
    movement_type: MovementType.PURCHASE,
    quantity: 0,
    unit_cost: undefined,
    reference_number: '',
    notes: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const router = useRouter();
  // Get user from auth context at the top level
  const { user } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Use getProducts for admin users, getOwnedProducts for regular users
        const [productsResponse, warehousesResponse] = await Promise.all([
          user?.is_admin 
            ? productService.getProducts({ page: 1, page_size: 100})
            : productService.getOwnedProducts({ page: 1, page_size: 100}),
          warehouseService.getWarehouses()
        ]);
        
        console.log('Products response:', productsResponse);
        console.log('Warehouses response:', warehousesResponse);
        
        if (!productsResponse?.items) {
          throw new Error('Products data is invalid');
        }
        
        if (!Array.isArray(warehousesResponse)) {
          throw new Error('Warehouses data is invalid');
        }
        
        setProducts(productsResponse.items);
        setWarehouses(warehousesResponse);
        
        console.log('Set products:', productsResponse.items.length);
        console.log('Set warehouses:', warehousesResponse.length);
      } catch (error) {
        console.error('Error fetching data:', error);
        toast.error(error instanceof Error ? error.message : 'Failed to load form data');
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
      case 'warehouse_id':
        if (!value || value === 0) {
          return 'Please select a warehouse';
        }
        return '';
      case 'quantity':
        if (value === undefined || value === null || value === 0) {
          return 'Quantity is required';
        }
        // For adjustments, allow negative values
        if (formData.movement_type === MovementType.ADJUSTMENT) {
          if (value === 0) {
            return 'Adjustment quantity cannot be zero';
          }
        } else {
          // For all other movement types, quantity must be positive
          if (value <= 0) {
            return 'Quantity must be greater than 0';
          }
        }
        return '';
      case 'unit_cost':
        if (value !== undefined && value < 0) {
          return 'Unit cost cannot be negative';
        }
        return '';
      default:
        return '';
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    let processedValue: any = value;

    if (name === 'product_id' || name === 'warehouse_id') {
      processedValue = parseInt(value);
    } else if (name === 'quantity') {
      processedValue = parseInt(value);
    } else if (name === 'unit_cost') {
      processedValue = value === '' ? undefined : parseFloat(value);
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
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
    
    const error = validateField(name, name === 'product_id' || name === 'warehouse_id' ? parseInt(value) : value);
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
      await stockMovementService.createStockMovement(formData);
      toast.success('Stock movement recorded successfully!');
      router.push('/stock-movements');
    } catch (error) {
      console.error('Error creating stock movement:', error);
      toast.error('Failed to record stock movement. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getMovementTypeLabel = (type: MovementType): string => {
    const labels = {
      [MovementType.PURCHASE]: 'Purchase',
      [MovementType.SALE]: 'Sale',
      [MovementType.ADJUSTMENT]: 'Inventory Adjustment',
      [MovementType.DAMAGED]: 'Damaged/Loss',
      [MovementType.RETURN]: 'Return',
      [MovementType.TRANSFER_IN]: 'Transfer In',
      [MovementType.TRANSFER_OUT]: 'Transfer Out'
    };
    return labels[type] || type;
  };

  const getMovementTypeColor = (type: MovementType): string => {
    const inboundTypes = [MovementType.PURCHASE, MovementType.RETURN, MovementType.TRANSFER_IN];
    return inboundTypes.includes(type) ? 'text-green-600' : 'text-red-600';
  };

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
            href="/stock-movements"
            className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors duration-200"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Stock Movements
          </Link>
          <div className="mt-4">
            <h1 className="text-3xl font-bold text-gray-900">Record Stock Movement</h1>
            <p className="mt-2 text-sm text-gray-600">
              Track inventory changes for purchases, sales, adjustments, and transfers.
            </p>
          </div>
        </div>

        {/* Form Container */}
        <div className="bg-white shadow-xl rounded-2xl overflow-hidden">
          {/* Info Message for No Products */}
          {products.length === 0 && (
            <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-6">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-amber-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-amber-700">
                    <strong>No products available!</strong> You need to create products before recording stock movements. 
                    Only products you created can be used for stock movements.{' '}
                    <Link href="/products/new" className="font-medium underline hover:text-amber-800">
                      Create a product first
                    </Link>
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Form Header */}
          <div className="bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-4">
            <div className="flex items-center">
              <ArrowUpDown className="h-6 w-6 text-white mr-3" />
              <h2 className="text-xl font-semibold text-white">Stock Movement Details</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="p-8 space-y-8">
            {/* Product & Warehouse Selection */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <Package className="h-5 w-5 mr-2 text-indigo-500" />
                Product & Location
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Product Selection */}
                <div className="space-y-1">
                  <label htmlFor="product_id" className="block text-sm font-semibold text-gray-700">
                    Product <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <select
                      name="product_id"
                      id="product_id"
                      required
                      className={`block w-full px-4 py-3 text-gray-900 border-2 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent appearance-none bg-white ${
                        errors.product_id && touched.product_id
                          ? 'border-red-300 bg-red-50 focus:ring-red-500'
                          : 'border-gray-200 hover:border-gray-300 focus:border-indigo-500'
                      }`}
                      value={formData.product_id}
                      onChange={handleChange}
                      onBlur={handleBlur}
                    >
                      <option value={0}>
                        {products.length === 0 ? 'No products owned - create products first' : 'Select a product...'}
                      </option>
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

                {/* Warehouse Selection */}
                <div className="space-y-1">
                  <label htmlFor="warehouse_id" className="block text-sm font-semibold text-gray-700">
                    Warehouse <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <select
                      name="warehouse_id"
                      id="warehouse_id"
                      required
                      className={`block w-full px-4 py-3 text-gray-900 border-2 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent appearance-none bg-white ${
                        errors.warehouse_id && touched.warehouse_id
                          ? 'border-red-300 bg-red-50 focus:ring-red-500'
                          : 'border-gray-200 hover:border-gray-300 focus:border-indigo-500'
                      }`}
                      value={formData.warehouse_id}
                      onChange={handleChange}
                      onBlur={handleBlur}
                    >
                      <option value={0}>Select a warehouse...</option>
                      {warehouses.map((warehouse) => (
                        <option key={warehouse.id} value={warehouse.id}>
                          {warehouse.name} - {warehouse.location}
                        </option>
                      ))}
                    </select>
                    <WarehouseIcon className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
                  </div>
                  {errors.warehouse_id && touched.warehouse_id && (
                    <p className="text-sm text-red-600 flex items-center mt-1">
                      <span className="w-1 h-1 bg-red-600 rounded-full mr-2"></span>
                      {errors.warehouse_id}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Movement Details */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <ArrowUpDown className="h-5 w-5 mr-2 text-indigo-500" />
                Movement Details
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Movement Type */}
                <div className="space-y-1">
                  <label htmlFor="movement_type" className="block text-sm font-semibold text-gray-700">
                    Movement Type <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <select
                      name="movement_type"
                      id="movement_type"
                      required
                      className={`block w-full px-4 py-3 text-gray-900 border-2 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent appearance-none bg-white ${getMovementTypeColor(formData.movement_type)}`}
                      value={formData.movement_type}
                      onChange={handleChange}
                      onBlur={handleBlur}
                    >
                      {Object.values(MovementType).map((type) => (
                        <option key={type} value={type}>
                          {getMovementTypeLabel(type)}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Quantity */}
                <div className="space-y-1">
                  <label htmlFor="quantity" className="block text-sm font-semibold text-gray-700">
                    Quantity <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="quantity"
                    id="quantity"
                    required
                    min={formData.movement_type === MovementType.ADJUSTMENT ? undefined : "1"}
                    className={`block w-full px-4 py-3 text-gray-900 border-2 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                      errors.quantity && touched.quantity
                        ? 'border-red-300 bg-red-50 focus:ring-red-500'
                        : 'border-gray-200 hover:border-gray-300 focus:border-indigo-500'
                    }`}
                    placeholder={formData.movement_type === MovementType.ADJUSTMENT ? "Enter positive to add, negative to subtract" : "0"}
                    value={formData.quantity || ''}
                    onChange={handleChange}
                    onBlur={handleBlur}
                  />
                  {/* Help text explaining quantity logic */}
                  <p className="text-xs text-gray-500 mt-1">
                    {formData.movement_type === MovementType.PURCHASE && "Will be added to inventory (+)"}
                    {formData.movement_type === MovementType.SALE && "Will be subtracted from inventory (-)"}
                    {formData.movement_type === MovementType.RETURN && "Will be added to inventory (+)"}
                    {formData.movement_type === MovementType.DAMAGED && "Will be subtracted from inventory (-)"}
                    {formData.movement_type === MovementType.TRANSFER_IN && "Will be added to inventory (+)"}
                    {formData.movement_type === MovementType.TRANSFER_OUT && "Will be subtracted from inventory (-)"}
                    {formData.movement_type === MovementType.ADJUSTMENT && "Enter positive to add, negative to subtract"}
                  </p>
                  {errors.quantity && touched.quantity && (
                    <p className="text-sm text-red-600 flex items-center mt-1">
                      <span className="w-1 h-1 bg-red-600 rounded-full mr-2"></span>
                      {errors.quantity}
                    </p>
                  )}
                </div>

                {/* Unit Cost */}
                <div className="space-y-1">
                  <label htmlFor="unit_cost" className="block text-sm font-semibold text-gray-700">
                    Unit Cost (Optional)
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <DollarSign className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type="number"
                      name="unit_cost"
                      id="unit_cost"
                      step="0.01"
                      min="0"
                      className={`block w-full pl-12 pr-4 py-3 text-gray-900 border-2 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                        errors.unit_cost && touched.unit_cost
                          ? 'border-red-300 bg-red-50 focus:ring-red-500'
                          : 'border-gray-200 hover:border-gray-300 focus:border-indigo-500'
                      }`}
                      placeholder="0.00"
                      value={formData.unit_cost || ''}
                      onChange={handleChange}
                      onBlur={handleBlur}
                    />
                  </div>
                  {errors.unit_cost && touched.unit_cost && (
                    <p className="text-sm text-red-600 flex items-center mt-1">
                      <span className="w-1 h-1 bg-red-600 rounded-full mr-2"></span>
                      {errors.unit_cost}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Reference & Notes */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <FileText className="h-5 w-5 mr-2 text-indigo-500" />
                Additional Information
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Reference Number */}
                <div className="space-y-1">
                  <label htmlFor="reference_number" className="block text-sm font-semibold text-gray-700">
                    Reference Number (Optional)
                  </label>
                  <input
                    type="text"
                    name="reference_number"
                    id="reference_number"
                    className="block w-full px-4 py-3 text-gray-900 border-2 border-gray-200 rounded-xl shadow-sm transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="e.g., PO-001, INV-123..."
                    value={formData.reference_number}
                    onChange={handleChange}
                    onBlur={handleBlur}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Purchase order, invoice, or other reference
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
                    className="block w-full px-4 py-3 text-gray-900 border-2 border-gray-200 rounded-xl shadow-sm transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                    placeholder="Additional notes or comments..."
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
                href="/stock-movements"
                className="inline-flex justify-center items-center px-6 py-3 border-2 border-gray-300 rounded-xl shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-all duration-200"
              >
                Cancel
              </Link>
              <button
                type="submit"
                disabled={isLoading || products.length === 0}
                className="inline-flex justify-center items-center px-8 py-3 border-2 border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Recording Movement...
                  </>
                ) : (
                  <>
                    <Save className="h-5 w-5 mr-2" />
                    Record Movement
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