'use client';

import { AuthProvider } from '@/context/AuthContext';
import Layout from '@/components/Layout';
import StockMovementForm from '@/components/StockMovementForm';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Toaster } from 'react-hot-toast';

export default function NewStockMovementPage() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <Layout>
          <Toaster position="top-right" />
          <StockMovementForm />
        </Layout>
      </ProtectedRoute>
    </AuthProvider>
  );
}