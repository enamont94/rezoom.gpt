# Rezoom.ai Setup Script for Windows PowerShell
# This script sets up the development environment for Rezoom.ai

param(
    [switch]$SkipDocker,
    [switch]$SkipNode,
    [switch]$SkipPython
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$White = "White"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# Check if Docker is installed
function Test-Docker {
    Write-Status "Checking Docker installation..."
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        Write-Host "Download from: https://www.docker.com/products/docker-desktop"
        exit 1
    }
    
    if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    }
    
    Write-Success "Docker and Docker Compose are installed"
}

# Check if Node.js is installed
function Test-Node {
    Write-Status "Checking Node.js installation..."
    
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Warning "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    }
    
    $nodeVersion = node --version
    Write-Success "Node.js $nodeVersion is installed"
}

# Check if Python is installed
function Test-Python {
    Write-Status "Checking Python installation..."
    
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Error "Python is not installed. Please install Python 3.11+ from https://python.org/"
        exit 1
    }
    
    $pythonVersion = python --version
    Write-Success "$pythonVersion is installed"
}

# Create necessary directories
function New-Directories {
    Write-Status "Creating necessary directories..."
    
    New-Item -ItemType Directory -Force -Path "backend\db" | Out-Null
    New-Item -ItemType Directory -Force -Path "backend\tmp" | Out-Null
    New-Item -ItemType Directory -Force -Path "backend\logs" | Out-Null
    New-Item -ItemType Directory -Force -Path "frontend\.next" | Out-Null
    
    Write-Success "Directories created"
}

# Setup environment files
function Set-EnvironmentFiles {
    Write-Status "Setting up environment files..."
    
    # Backend environment
    if (-not (Test-Path "backend\.env")) {
        Copy-Item "backend\env.example" "backend\.env"
        Write-Success "Backend .env file created"
    } else {
        Write-Warning "Backend .env file already exists"
    }
    
    # Frontend environment
    if (-not (Test-Path "frontend\.env.local")) {
        @"
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-key
"@ | Out-File -FilePath "frontend\.env.local" -Encoding UTF8
        Write-Success "Frontend .env.local file created"
    } else {
        Write-Warning "Frontend .env.local file already exists"
    }
}

# Install Python dependencies
function Install-PythonDependencies {
    Write-Status "Installing Python dependencies..."
    
    Set-Location backend
    
    if (-not (Test-Path "venv")) {
        python -m venv venv
        Write-Success "Python virtual environment created"
    }
    
    & "venv\Scripts\Activate.ps1"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    Write-Success "Python dependencies installed"
    
    Set-Location ..
}

# Install Node.js dependencies
function Install-NodeDependencies {
    Write-Status "Installing Node.js dependencies..."
    
    Set-Location frontend
    npm install
    Write-Success "Node.js dependencies installed"
    Set-Location ..
}

# Setup Ollama
function Set-Ollama {
    Write-Status "Setting up Ollama..."
    
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        Write-Warning "Ollama is not installed. Please install Ollama from https://ollama.ai/"
        Write-Host "After installation, run: ollama pull mistral"
    } else {
        Write-Success "Ollama is ready"
        Write-Status "To download Mistral model, run: ollama pull mistral"
    }
}

# Build Docker images
function Build-Docker {
    Write-Status "Building Docker images..."
    
    docker-compose build
    Write-Success "Docker images built"
}

# Start services
function Start-Services {
    Write-Status "Starting services..."
    
    docker-compose up -d
    Write-Success "Services started"
    
    # Wait for services to be ready
    Write-Status "Waiting for services to be ready..."
    Start-Sleep -Seconds 10
    
    # Check service health
    Test-ServiceHealth
}

# Check service health
function Test-ServiceHealth {
    Write-Status "Checking service health..."
    
    # Check backend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Backend is healthy"
        }
    } catch {
        Write-Warning "Backend is not responding"
    }
    
    # Check frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Frontend is healthy"
        }
    } catch {
        Write-Warning "Frontend is not responding"
    }
    
    # Check Ollama
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Ollama is healthy"
        }
    } catch {
        Write-Warning "Ollama is not responding"
    }
}

# Display final information
function Show-FinalInfo {
    Write-Host ""
    Write-Host "🎉 Rezoom.ai setup completed!" -ForegroundColor $Green
    Write-Host ""
    Write-Host "📋 Service URLs:" -ForegroundColor $Blue
    Write-Host "  • Frontend: http://localhost:3000"
    Write-Host "  • Backend API: http://localhost:8000"
    Write-Host "  • API Docs: http://localhost:8000/docs"
    Write-Host "  • Ollama: http://localhost:11434"
    Write-Host ""
    Write-Host "🔧 Next steps:" -ForegroundColor $Yellow
    Write-Host "  1. Download Mistral model: ollama pull mistral"
    Write-Host "  2. Configure environment variables in backend\.env"
    Write-Host "  3. Configure Supabase in frontend\.env.local"
    Write-Host "  4. Start developing!"
    Write-Host ""
    Write-Host "📚 Documentation:" -ForegroundColor $Blue
    Write-Host "  • README.md - Complete setup guide"
    Write-Host "  • http://localhost:8000/docs - API documentation"
    Write-Host ""
    Write-Host "🛠️ Development commands:" -ForegroundColor $Yellow
    Write-Host "  • docker-compose up -d     # Start all services"
    Write-Host "  • docker-compose down      # Stop all services"
    Write-Host "  • docker-compose logs -f   # View logs"
    Write-Host "  • docker-compose ps        # Check service status"
    Write-Host ""
}

# Main execution
function Main {
    Write-Status "Starting Rezoom.ai setup..."
    
    if (-not $SkipDocker) { Test-Docker }
    if (-not $SkipNode) { Test-Node }
    if (-not $SkipPython) { Test-Python }
    
    New-Directories
    Set-EnvironmentFiles
    Install-PythonDependencies
    Install-NodeDependencies
    Set-Ollama
    Build-Docker
    Start-Services
    Show-FinalInfo
}

# Run main function
Main
