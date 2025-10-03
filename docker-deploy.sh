#!/bin/bash

# Docker Startup Script for Inventory Management System
# Author: DevOps Engineer
# Description: Quick deployment script with environment setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "🚀 Inventory Management System Docker Deployment"
    echo "=================================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        echo "Please install Docker from https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_step "Prerequisites check passed!"
}

setup_environment() {
    print_step "Setting up environment..."
    
    if [ ! -f .env ]; then
        print_warning ".env file not found, creating from template..."
        cp .env.template .env
        echo "Please edit .env file with your configuration and run this script again."
        echo "Important: Change the SECRET_KEY and database passwords!"
        exit 0
    else
        print_step "Environment file found!"
    fi
}

build_and_deploy() {
    print_step "Building and deploying services..."
    
    # Stop any running containers
    docker-compose down
    
    # Build and start services
    if [ "$1" == "dev" ]; then
        print_step "Starting in development mode with hot-reload..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
    else
        print_step "Starting in production mode..."
        docker-compose up --build -d
    fi
}

show_status() {
    print_step "Checking service status..."
    
    # Wait a moment for containers to start
    sleep 5
    
    echo ""
    echo "Service Status:"
    docker-compose ps
    
    echo ""
    echo "Service Health:"
    
    # Check backend health
    echo -n "Backend API: "
    if curl -f -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN} Healthy${NC}"
    else
        echo -e "${RED} Unhealthy${NC}"
    fi
    
    # Check frontend
    echo -n "Frontend: "
    if curl -f -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN} Healthy${NC}"
    else
        echo -e "${RED} Unhealthy${NC}"
    fi
}

show_access_info() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "🎉 Deployment Complete!"
    echo "=================================================="
    echo ""
    echo "Access your application:"
    echo " Frontend:       http://localhost:3000"
    echo " Backend API:    http://localhost:8000"
    echo " API Docs:       http://localhost:8000/docs"
    echo "  pgAdmin:       http://localhost:8080 (admin tools)"
    echo ""
    echo "Useful commands:"
    echo " View logs:      docker-compose logs -f"
    echo " Stop services:  docker-compose down"
    echo " Restart:        docker-compose restart"
    echo ""
    echo -e "${NC}"
}

# Main execution
main() {
    print_header
    
    # Handle command line arguments
    case "${1:-}" in
        "dev")
            MODE="dev"
            ;;
        "prod"|"production"|"")
            MODE="prod"
            ;;
        "status")
            docker-compose ps
            exit 0
            ;;
        "logs")
            docker-compose logs -f
            exit 0
            ;;
        "stop")
            docker-compose down
            print_step "Services stopped!"
            exit 0
            ;;
        "clean")
            docker-compose down -v --remove-orphans
            docker system prune -f
            print_step "System cleaned!"
            exit 0
            ;;
        *)
            echo "Usage: $0 [dev|prod|status|logs|stop|clean]"
            echo ""
            echo "Commands:"
            echo "  dev     - Start in development mode"
            echo "  prod    - Start in production mode (default)"
            echo "  status  - Show service status"
            echo "  logs    - View service logs"
            echo "  stop    - Stop all services"
            echo "  clean   - Stop services and clean system"
            exit 1
            ;;
    esac
    
    check_prerequisites
    setup_environment
    build_and_deploy "$MODE"
    show_status
    show_access_info
}

# Run main function
main "$@"