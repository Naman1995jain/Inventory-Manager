'use client';

import { AuthProvider } from '@/context/AuthContext';
import Layout from '@/components/Layout';
import StockMovementList from '@/components/StockMovementList';
import ProtectedRoute from '@/components/ProtectedRoute';
import WebSocketStatus from '@/components/WebSocketStatus';
import { Toaster } from 'react-hot-toast';

export default function StockMovementsPage() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <Layout>
          <Toaster position="top-right" />
          <WebSocketStatus showText={false} />
          <StockMovementList />
        </Layout>
      </ProtectedRoute>
    </AuthProvider>
  );
}