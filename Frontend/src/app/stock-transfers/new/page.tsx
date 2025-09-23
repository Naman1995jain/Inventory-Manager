'use client';

import { AuthProvider } from '@/context/AuthContext';
import Layout from '@/components/Layout';
import StockTransferForm from '@/components/StockTransferForm';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Toaster } from 'react-hot-toast';

export default function NewStockTransferPage() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <Layout>
          <Toaster position="top-right" />
          <StockTransferForm />
        </Layout>
      </ProtectedRoute>
    </AuthProvider>
  );
}