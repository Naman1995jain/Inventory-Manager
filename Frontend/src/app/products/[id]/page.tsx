'use client';

import { AuthProvider } from '@/context/AuthContext';
import Layout from '@/components/Layout';
import ProductDetail from '@/components/ProductDetail';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Toaster } from 'react-hot-toast';

interface ProductDetailPageProps {
  params: {
    id: string;
  };
}

export default function ProductDetailPage({ params }: ProductDetailPageProps) {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <Layout>
          <Toaster position="top-right" />
          <ProductDetail productId={parseInt(params.id)} />
        </Layout>
      </ProtectedRoute>
    </AuthProvider>
  );
}