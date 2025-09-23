'use client';

import React, { useState, useEffect } from 'react';
import { Product, ProductUpdate } from '@/types';
import { productService } from '@/lib/services';
import { ArrowLeft, Save, Package, DollarSign, Tag, FileText, Ruler, Edit } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';

interface ProductEditProps {
  productId: number;
}

export default function ProductEdit({ productId }: ProductEditProps) {
  const [product, setProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState<ProductUpdate>({
    name: '',
    description: '',
    sku: '',
    category: '',
    unit_price: undefined,
    unit_of_measure: '',
    is_active: true
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const router = useRouter();

  // Validation function
  const validateField = (name: string, value: any): string => {
    switch (name) {
      case 'name':
        if (!value || value.trim().length < 2) {
          return 'Product name must be at least 2 characters long';
        }
        return '';
      case 'sku':
        if (!value || value.trim().length < 3) {
          return 'SKU must be at least 3 characters long';
        }
        if (!/^[A-Za-z0-9-_]+$/.test(value)) {
          return 'SKU can only contain letters, numbers, hyphens, and underscores';
        }
        return '';
      case 'unit_price':
        if (value !== undefined && value < 0) {
          return 'Price cannot be negative';
        }
        return '';
      default:
        return '';
    }
  };

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setIsLoading(true);
        const productData = await productService.getProduct(productId);
        setProduct(productData);
        setFormData({
          name: productData.name,
          description: productData.description || '',
          sku: productData.sku,
          category: productData.category || '',
          unit_price: productData.unit_price,
          unit_of_measure: productData.unit_of_measure || '',
          is_active: productData.is_active
        });
      } catch (error) {
        toast.error('Product not found');
        router.push('/products');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProduct();
  }, [productId, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    // Validate all fields
    const newErrors: Record<string, string> = {};
    Object.entries(formData).forEach(([key, value]) => {
      const error = validateField(key, value);
      if (error) newErrors[key] = error;
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setTouched(Object.keys(formData).reduce((acc, key) => ({ ...acc, [key]: true }), {}));
      setIsSaving(false);
      return;
    }

    try {
      await productService.updateProduct(productId, formData);
      toast.success('Product updated successfully!');
      router.push(`/products/${productId}`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update product');
    } finally {
      setIsSaving(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    const processedValue = name === 'unit_price' ? (value === '' ? undefined : parseFloat(value)) : value;
    
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
    
    const error = validateField(name, value);
    setErrors(prev => ({
      ...prev,
      [name]: error
    }));
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          <p className="mt-2 text-sm text-gray-500">Loading product...</p>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Package className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Product not found</h3>
          <p className="mt-1 text-sm text-gray-500">The product you're trying to edit doesn't exist.</p>
          <div className="mt-6">
            <Link
              href="/products"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Products
            </Link>
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
            href={`/products/${productId}`}
            className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors duration-200"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Product Details
          </Link>
          <div className="mt-4">
            <h1 className="text-3xl font-bold text-gray-900">Edit Product</h1>
            <p className="mt-2 text-sm text-gray-600">
              Update product information for {product.name}.
            </p>
          </div>
        </div>

        {/* Form Container */}
        <div className="bg-white shadow-xl rounded-2xl overflow-hidden">
          {/* Form Header */}
          <div className="bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-4">
            <div className="flex items-center">
              <Edit className="h-6 w-6 text-white mr-3" />
              <h2 className="text-xl font-semibold text-white">Update Product Information</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="p-8 space-y-8">
            {/* Basic Information Section */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <Tag className="h-5 w-5 mr-2 text-indigo-500" />
                Basic Information
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Product Name */}
                <div className="space-y-1">
                  <label htmlFor="name" className="block text-sm font-semibold text-gray-700">
                    Product Name <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      name="name"
                      id="name"
                      required
                      className={`block w-full px-4 py-3 text-gray-900 border-2 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                        errors.name && touched.name
                          ? 'border-red-300 bg-red-50 focus:ring-red-500'
                          : 'border-gray-200 hover:border-gray-300 focus:border-indigo-500'
                      }`}
                      placeholder="Enter product name..."
                      value={formData.name}
                      onChange={handleChange}
                      onBlur={handleBlur}
                    />
                    <Package className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  </div>
                  {errors.name && touched.name && (
                    <p className="text-sm text-red-600 flex items-center mt-1">
                      <span className="w-1 h-1 bg-red-600 rounded-full mr-2"></span>
                      {errors.name}
                    </p>
                  )}
                </div>

                {/* SKU */}
                <div className="space-y-1">
                  <label htmlFor="sku" className="block text-sm font-semibold text-gray-700">
                    SKU (Stock Keeping Unit) <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      name="sku"
                      id="sku"
                      required
                      className={`block w-full px-4 py-3 text-gray-900 border-2 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                        errors.sku && touched.sku
                          ? 'border-red-300 bg-red-50 focus:ring-red-500'
                          : 'border-gray-200 hover:border-gray-300 focus:border-indigo-500'
                      }`}
                      placeholder="e.g., PROD-001, ABC123..."
                      value={formData.sku}
                      onChange={handleChange}
                      onBlur={handleBlur}
                    />
                    <Tag className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  </div>
                  {errors.sku && touched.sku && (
                    <p className="text-sm text-red-600 flex items-center mt-1">
                      <span className="w-1 h-1 bg-red-600 rounded-full mr-2"></span>
                      {errors.sku}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    Unique identifier for inventory tracking
                  </p>
                </div>
              </div>
            </div>

            {/* Category and Measurement Section */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <Ruler className="h-5 w-5 mr-2 text-indigo-500" />
                Classification & Measurement
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Category */}
                <div className="space-y-1">
                  <label htmlFor="category" className="block text-sm font-semibold text-gray-700">
                    Category
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      name="category"
                      id="category"
                      className="block w-full px-4 py-3 text-gray-900 border-2 border-gray-200 rounded-xl shadow-sm transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="e.g., Electronics, Clothing, Food..."
                      value={formData.category}
                      onChange={handleChange}
                      onBlur={handleBlur}
                    />
                    <Tag className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  </div>
                </div>

                {/* Unit of Measure */}
                <div className="space-y-1">
                  <label htmlFor="unit_of_measure" className="block text-sm font-semibold text-gray-700">
                    Unit of Measure
                  </label>
                  <div className="relative">
                    <select
                      name="unit_of_measure"
                      id="unit_of_measure"
                      className="block w-full px-4 py-3 text-gray-900 border-2 border-gray-200 rounded-xl shadow-sm transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent appearance-none bg-white"
                      value={formData.unit_of_measure}
                      onChange={handleChange}
                      onBlur={handleBlur}
                    >
                      <option value="">Select unit...</option>
                      <option value="piece">Piece</option>
                      <option value="kg">Kilogram (kg)</option>
                      <option value="liter">Liter (L)</option>
                      <option value="meter">Meter (m)</option>
                      <option value="box">Box</option>
                      <option value="pack">Pack</option>
                      <option value="dozen">Dozen</option>
                      <option value="pair">Pair</option>
                    </select>
                    <Ruler className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
                  </div>
                </div>
              </div>
            </div>

            {/* Pricing Section */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <DollarSign className="h-5 w-5 mr-2 text-indigo-500" />
                Pricing Information
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Unit Price */}
                <div className="space-y-1">
                  <label htmlFor="unit_price" className="block text-sm font-semibold text-gray-700">
                    Unit Price (Optional)
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <DollarSign className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type="number"
                      name="unit_price"
                      id="unit_price"
                      step="0.01"
                      min="0"
                      className={`block w-full pl-12 pr-4 py-3 text-gray-900 border-2 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                        errors.unit_price && touched.unit_price
                          ? 'border-red-300 bg-red-50 focus:ring-red-500'
                          : 'border-gray-200 hover:border-gray-300 focus:border-indigo-500'
                      }`}
                      placeholder="0.00"
                      value={formData.unit_price || ''}
                      onChange={handleChange}
                      onBlur={handleBlur}
                    />
                  </div>
                  {errors.unit_price && touched.unit_price && (
                    <p className="text-sm text-red-600 flex items-center mt-1">
                      <span className="w-1 h-1 bg-red-600 rounded-full mr-2"></span>
                      {errors.unit_price}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    Leave empty if price varies or is not applicable
                  </p>
                </div>

                {/* Status */}
                <div className="space-y-1">
                  <label htmlFor="is_active" className="block text-sm font-semibold text-gray-700">
                    Product Status
                  </label>
                  <div className="relative">
                    <select
                      name="is_active"
                      id="is_active"
                      className="block w-full px-4 py-3 text-gray-900 border-2 border-gray-200 rounded-xl shadow-sm transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent appearance-none bg-white"
                      value={formData.is_active ? 'true' : 'false'}
                      onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.value === 'true' }))}
                    >
                      <option value="true">Active</option>
                      <option value="false">Inactive</option>
                    </select>
                    <Package className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Inactive products are hidden from most views
                  </p>
                </div>
              </div>
            </div>

            {/* Description Section */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <FileText className="h-5 w-5 mr-2 text-indigo-500" />
                Description & Notes
              </h3>
              <div className="space-y-1">
                <label htmlFor="description" className="block text-sm font-semibold text-gray-700">
                  Product Description (Optional)
                </label>
                <textarea
                  name="description"
                  id="description"
                  rows={4}
                  className="block w-full px-4 py-3 text-gray-900 border-2 border-gray-200 rounded-xl shadow-sm transition-all duration-200 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                  placeholder="Enter detailed description, specifications, features, or any additional notes about this product..."
                  value={formData.description}
                  onChange={handleChange}
                  onBlur={handleBlur}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Provide details that will help identify and manage this product
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row justify-end space-y-3 sm:space-y-0 sm:space-x-4 pt-6 border-t border-gray-200">
              <Link
                href={`/products/${productId}`}
                className="inline-flex justify-center items-center px-6 py-3 border-2 border-gray-300 rounded-xl shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-all duration-200"
              >
                Cancel
              </Link>
              <button
                type="submit"
                disabled={isSaving}
                className="inline-flex justify-center items-center px-8 py-3 border-2 border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100"
              >
                {isSaving ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Updating Product...
                  </>
                ) : (
                  <>
                    <Save className="h-5 w-5 mr-2" />
                    Update Product
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