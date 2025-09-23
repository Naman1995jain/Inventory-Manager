'use client';

import { AuthProvider } from '@/context/AuthContext';
import Layout from '@/components/Layout';
import ProductForm from '@/components/ProductForm';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Toaster } from 'react-hot-toast';

export default function NewProductPage() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <Layout>
          <Toaster position="top-right" />
          <ProductForm />
        </Layout>
      </ProtectedRoute>
    </AuthProvider>
  );
}