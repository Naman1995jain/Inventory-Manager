# Inventory Management Frontend

A modern Next.js frontend application for the Inventory Management System built with TypeScript, Tailwind CSS, and React.

## Features

- **Authentication**: User registration and login with JWT tokens
- **Product Management**: Create, read, update, and delete products with stock tracking
- **Stock Movements**: Track inventory changes (purchases, sales, adjustments, etc.)
- **Stock Transfers**: Manage inventory transfers between warehouses (coming soon)
- **Dashboard**: Overview of inventory metrics and quick actions
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Context + React Query
- **Forms**: React Hook Form
- **Notifications**: React Hot Toast
- **Authentication**: JWT with cookies

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

1. Clone the repository and navigate to the frontend directory
2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy environment variables:
   ```bash
   cp .env.local.example .env.local
   ```

4. Update the API URL in `.env.local` if needed:
   ```
   API_URL=http://localhost:8000/api/v1
   ```

5. Start the development server:
   ```bash
   npm run dev
   ```

6. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── dashboard/         # Dashboard page
│   ├── login/            # Login page
│   ├── products/         # Products pages
│   ├── register/         # Registration page
│   ├── stock-movements/  # Stock movements pages
│   └── stock-transfers/  # Stock transfers pages
├── components/           # React components
├── context/             # React contexts (Auth)
├── lib/                # Utilities and services
│   ├── api.ts          # Axios configuration
│   └── services.ts     # API service functions
└── types/              # TypeScript type definitions
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## API Integration

The frontend communicates with the backend API using the following endpoints:

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Products
- `GET /products/` - List products (paginated)
- `POST /products/` - Create product
- `GET /products/{id}` - Get product details
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product

### Stock Movements
- `GET /stock-movements/` - List stock movements
- `POST /stock-movements/` - Create stock movement

### Stock Transfers
- `GET /stock-transfers/` - List stock transfers
- `POST /stock-transfers/` - Create stock transfer
- `PUT /stock-transfers/{id}/complete` - Complete transfer
- `PUT /stock-transfers/{id}/cancel` - Cancel transfer

## Features Overview

### Authentication
- JWT-based authentication with automatic token refresh
- Protected routes requiring authentication
- User registration and login forms
- Automatic redirect to login on token expiration

### Product Management
- Create products with SKU, name, description, price, and category
- View products in a paginated table with search functionality
- Edit and delete products
- Track stock levels across warehouses

### Stock Movements
- Record various types of inventory movements
- View movement history with filtering and search
- Support for purchases, sales, adjustments, damages, returns, and transfers

### Dashboard
- Overview of key inventory metrics
- Quick action buttons for common tasks
- Statistics cards showing totals and trends

## Environment Variables

- `API_URL` - Backend API base URL (default: http://localhost:8000/api/v1)
- `NODE_ENV` - Environment (development/production)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.