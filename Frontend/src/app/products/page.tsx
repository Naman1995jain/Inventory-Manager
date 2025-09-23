'use client';

import { AuthProvider } from '@/context/AuthContext';
import Layout from '@/components/Layout';
import ProductList from '@/components/ProductList';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Toaster } from 'react-hot-toast';

export default function ProductsPage() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <Layout>
          <Toaster position="top-right" />
          <ProductList />
        </Layout>
      </ProtectedRoute>
    </AuthProvider>
  );
}