import api from './api';
import { 
  UserCreate, 
  UserLogin, 
  Token, 
  User,
  Product,
  ProductCreate,
  ProductUpdate,
  ProductListResponse,
  ProductWithStock,
  StockMovement,
  StockMovementCreate,
  StockMovementListResponse,
  StockTransfer,
  StockTransferCreate,
  StockTransferListResponse,
  PaginationParams,
  Warehouse
} from '@/types';

// Auth Services
export const authService = {
  async register(userData: UserCreate): Promise<User> {
    const response = await api.post<User>('/auth/register', userData);
    return response.data;
  },

  async login(userData: UserLogin): Promise<Token> {
    const response = await api.post<Token>('/auth/login', userData);
    return response.data;
  },
};

// Product Services
export const productService = {
  async getProducts(params: Partial<PaginationParams> = {}): Promise<ProductListResponse> {
    const response = await api.get<ProductListResponse>('/products/', { params });
    return response.data;
  },

  async getOwnedProducts(params: Partial<PaginationParams> = {}): Promise<ProductListResponse> {
    const response = await api.get<ProductListResponse>('/products/owned', { params });
    return response.data;
  },

  async getProduct(id: number): Promise<ProductWithStock> {
    const response = await api.get<ProductWithStock>(`/products/${id}`);
    return response.data;
  },

  async createProduct(data: ProductCreate): Promise<Product> {
    const response = await api.post<Product>('/products/', data);
    return response.data;
  },

  async updateProduct(id: number, data: ProductUpdate): Promise<Product> {
    const response = await api.put<Product>(`/products/${id}`, data);
    return response.data;
  },

  async deleteProduct(id: number): Promise<void> {
    await api.delete(`/products/${id}`);
  },
};

// Stock Movement Services
export const stockMovementService = {
  async getStockMovements(params: Partial<PaginationParams> = {}): Promise<StockMovementListResponse> {
    const response = await api.get<StockMovementListResponse>('/stock-movements/', { params });
    return response.data;
  },

  async getPurchaseSaleMovements(): Promise<StockMovementListResponse> {
    const response = await api.get<StockMovementListResponse>('/stock-movements/purchase-sale');
    return response.data;
  },

  async createStockMovement(data: StockMovementCreate): Promise<StockMovement> {
    const response = await api.post<StockMovement>('/stock-movements/', data);
    return response.data;
  },
};

// Stock Transfer Services
export const stockTransferService = {
  async getStockTransfers(params: Partial<PaginationParams> = {}): Promise<StockTransferListResponse> {
    const response = await api.get<StockTransferListResponse>('/stock-transfers/', { params });
    return response.data;
  },

  async createStockTransfer(data: StockTransferCreate): Promise<StockTransfer> {
    const response = await api.post<StockTransfer>('/stock-transfers/', data);
    return response.data;
  },

  async completeStockTransfer(id: number): Promise<StockTransfer> {
    const response = await api.put<StockTransfer>(`/stock-transfers/${id}/complete`);
    return response.data;
  },

  async cancelStockTransfer(id: number): Promise<StockTransfer> {
    const response = await api.put<StockTransfer>(`/stock-transfers/${id}/cancel`);
    return response.data;
  },
};

// Warehouse Services
export const warehouseService = {
  async getWarehouses(): Promise<Warehouse[]> {
    const response = await api.get<Warehouse[]>('/warehouses/');
    return response.data;
  },

  async getWarehouse(id: number): Promise<Warehouse> {
    const response = await api.get<Warehouse>(`/warehouses/${id}`);
    return response.data;
  },
};