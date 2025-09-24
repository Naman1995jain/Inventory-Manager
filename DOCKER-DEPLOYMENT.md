# 🐳 Docker Deployment Guide

This guide will help you deploy the Inventory Management System using Docker and Docker Compose.

## 📋 Prerequisites

- Docker (v20.10 or higher)
- Docker Compose (v2.0 or higher)
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Inventory-Manager
```

### 2. Set Up Environment Variables
```bash
# Copy the environment template
cp .env.template .env

# Edit the .env file with your preferred settings
nano .env
```

### 3. Start the Application
```bash
# For production deployment
docker-compose up -d

# For development with hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **pgAdmin** (optional): http://localhost:8080

## 🏗️ Architecture Overview

The application consists of:

- **Frontend**: Next.js React application (Port 3000)
- **Backend**: FastAPI Python application (Port 8000)  
- **Database**: PostgreSQL (Port 5432)
- **pgAdmin**: Database administration tool (Port 8080, optional)

## 📂 Service Details

### Backend Service
- **Container**: `inventory-backend`
- **Build Context**: `./Backend`
- **Port**: 8000
- **Features**:
  - Automatic database initialization
  - Health checks
  - Persistent log storage
  - Non-root user execution

### Frontend Service
- **Container**: `inventory-frontend`
- **Build Context**: `./Frontend`
- **Port**: 3000
- **Features**:
  - Multi-stage build for optimization
  - Standalone Next.js deployment
  - Health checks
  - Non-root user execution

### PostgreSQL Service
- **Container**: `inventory-postgres`
- **Image**: `postgres:15-alpine`
- **Port**: 5432
- **Features**:
  - Persistent data storage
  - Health checks
  - Custom initialization scripts

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `postgres123` |
| `SECRET_KEY` | JWT secret key | Change in production |
| `API_PORT` | Backend API port | `8000` |
| `FRONTEND_PORT` | Frontend port | `3000` |
| `DEBUG` | Enable debug mode | `false` |

### Database Initialization

The backend automatically:
1. Waits for PostgreSQL to be ready
2. Creates required databases (`inventory_db`, `inventory_test_db`)
3. Sets up database tables and initial data
4. Starts the FastAPI application

## 🛠️ Management Commands

### Start Services
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# View logs
docker-compose logs -f backend
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ This will delete all data)
docker-compose down -v
```

### Rebuild Services
```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build backend

# Rebuild and start
docker-compose up -d --build
```

### Database Management
```bash
# Access PostgreSQL directly
docker-compose exec postgres psql -U postgres -d inventory_db

# View database logs
docker-compose logs postgres

# Backup database
docker-compose exec postgres pg_dump -U postgres inventory_db > backup.sql
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using the port
   lsof -i :8000
   
   # Change port in .env file
   API_PORT=8001
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL logs
   docker-compose logs postgres
   
   # Verify database is healthy
   docker-compose ps
   ```

3. **Permission Issues**
   ```bash
   # Fix volume permissions
   sudo chown -R $USER:$USER ./Backend/logs
   ```

### Health Checks

All services include health checks:
```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:8000/health
curl http://localhost:3000/
```

## 📊 Monitoring

### View Service Status
```bash
# All services status
docker-compose ps

# Resource usage
docker stats

# Service logs
docker-compose logs -f --tail=100
```

### Database Administration

Use pgAdmin for GUI database management:
1. Access http://localhost:8080
2. Login with credentials from `.env`
3. Add server: `postgres:5432`

## 🏭 Production Deployment

### Security Checklist
- [ ] Change default passwords
- [ ] Use strong `SECRET_KEY`
- [ ] Configure CORS origins properly
- [ ] Set up SSL/TLS certificates
- [ ] Use secrets management
- [ ] Configure firewall rules

### Performance Optimization
```bash
# Use production compose file
docker-compose -f docker-compose.yml up -d

# Scale services if needed
docker-compose up -d --scale backend=2
```

### Backup Strategy
```bash
# Regular database backup
docker-compose exec postgres pg_dump -U postgres inventory_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Volume backup
docker run --rm -v inventory-postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

## 🐛 Development Mode

For development with hot-reload:
```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f backend frontend
```

Development features:
- Source code mounting
- Hot-reload for both frontend and backend
- Debug mode enabled
- pgAdmin included by default

## 🔄 Updates

To update the application:
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify all services are healthy: `docker-compose ps`
3. Check environment variables: `cat .env`
4. Review this documentation

---

**Note**: Always backup your data before performing updates or maintenance operations.