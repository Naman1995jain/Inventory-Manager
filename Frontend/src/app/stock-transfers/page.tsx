'use client';

import { AuthProvider } from '@/context/AuthContext';
import Layout from '@/components/Layout';
import StockTransferList from '@/components/StockTransferList';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Toaster } from 'react-hot-toast';

export default function StockTransfersPage() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <Layout>
          <Toaster position="top-right" />
          <StockTransferList />
        </Layout>
      </ProtectedRoute>
    </AuthProvider>
  );
}