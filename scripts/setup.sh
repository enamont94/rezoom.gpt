#!/bin/bash

# Rezoom.ai Setup Script
# This script sets up the development environment for Rezoom.ai

set -e

echo "🚀 Setting up Rezoom.ai development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    if ! command -v node &> /dev/null; then
        print_warning "Node.js is not installed. Installing Node.js 18..."
        # Install Node.js 18 using NodeSource repository
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
    
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION is installed"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version)
    print_success "$PYTHON_VERSION is installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p backend/db
    mkdir -p backend/tmp
    mkdir -p backend/logs
    mkdir -p frontend/.next
    
    print_success "Directories created"
}

# Setup environment files
setup_env() {
    print_status "Setting up environment files..."
    
    # Backend environment
    if [ ! -f backend/.env ]; then
        cp backend/env.example backend/.env
        print_success "Backend .env file created"
    else
        print_warning "Backend .env file already exists"
    fi
    
    # Frontend environment
    if [ ! -f frontend/.env.local ]; then
        cat > frontend/.env.local << EOF
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-key
EOF
        print_success "Frontend .env.local file created"
    else
        print_warning "Frontend .env.local file already exists"
    fi
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Python virtual environment created"
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Python dependencies installed"
    cd ..
}

# Install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js dependencies..."
    
    cd frontend
    npm install
    print_success "Node.js dependencies installed"
    cd ..
}

# Setup Ollama
setup_ollama() {
    print_status "Setting up Ollama..."
    
    if ! command -v ollama &> /dev/null; then
        print_warning "Ollama is not installed. Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
    
    print_success "Ollama is ready"
    print_status "To download Mistral model, run: ollama pull mistral"
}

# Build Docker images
build_docker() {
    print_status "Building Docker images..."
    
    docker-compose build
    print_success "Docker images built"
}

# Start services
start_services() {
    print_status "Starting services..."
    
    docker-compose up -d
    print_success "Services started"
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    check_service_health
}

# Check service health
check_service_health() {
    print_status "Checking service health..."
    
    # Check backend
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Backend is healthy"
    else
        print_warning "Backend is not responding"
    fi
    
    # Check frontend
    if curl -f http://localhost:3000 &> /dev/null; then
        print_success "Frontend is healthy"
    else
        print_warning "Frontend is not responding"
    fi
    
    # Check Ollama
    if curl -f http://localhost:11434/api/tags &> /dev/null; then
        print_success "Ollama is healthy"
    else
        print_warning "Ollama is not responding"
    fi
}

# Display final information
display_info() {
    echo ""
    echo "🎉 Rezoom.ai setup completed!"
    echo ""
    echo "📋 Service URLs:"
    echo "  • Frontend: http://localhost:3000"
    echo "  • Backend API: http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/docs"
    echo "  • Ollama: http://localhost:11434"
    echo ""
    echo "🔧 Next steps:"
    echo "  1. Download Mistral model: ollama pull mistral"
    echo "  2. Configure environment variables in backend/.env"
    echo "  3. Configure Supabase in frontend/.env.local"
    echo "  4. Start developing!"
    echo ""
    echo "📚 Documentation:"
    echo "  • README.md - Complete setup guide"
    echo "  • http://localhost:8000/docs - API documentation"
    echo ""
    echo "🛠️ Development commands:"
    echo "  • docker-compose up -d     # Start all services"
    echo "  • docker-compose down      # Stop all services"
    echo "  • docker-compose logs -f   # View logs"
    echo "  • docker-compose ps        # Check service status"
    echo ""
}

# Main execution
main() {
    print_status "Starting Rezoom.ai setup..."
    
    check_docker
    check_node
    check_python
    create_directories
    setup_env
    install_python_deps
    install_node_deps
    setup_ollama
    build_docker
    start_services
    display_info
# }

# Run main function
main "$@"
