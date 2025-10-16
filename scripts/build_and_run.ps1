# ============================================
# Jatan Jewellery - Cross-Platform Build Script
# For Windows PowerShell
# ============================================

param(
  [Parameter(Position = 0)]
  [string]$Action = "up",

  [Parameter(Position = 1)]
  [string]$WithPgAdmin = "false"
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to print colored output
function Write-Info {
  param([string]$Message)
  Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
  param([string]$Message)
  Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
  param([string]$Message)
  Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-ErrorMsg {
  param([string]$Message)
  Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Banner
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Jatan Jewellery - Salary Management" -ForegroundColor Cyan
Write-Host "  Docker Deployment Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker installation
Write-Info "Checking Docker installation..."
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-ErrorMsg "Docker is not installed!"
  Write-Host ""
  Write-Host "Please install Docker Desktop for Windows:" -ForegroundColor Yellow
  Write-Host "  https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
  exit 1
}

$dockerVersion = docker --version
Write-Success "Docker is installed: $dockerVersion"

# Check Docker Compose
Write-Info "Checking Docker Compose..."
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
  if (-not (docker compose version 2>$null)) {
    Write-ErrorMsg "Docker Compose is not installed!"
    Write-Host ""
    Write-Host "Please install Docker Compose:" -ForegroundColor Yellow
    Write-Host "  https://docs.docker.com/compose/install/" -ForegroundColor Yellow
    exit 1
  }
}
Write-Success "Docker Compose is available"

# Check if Docker daemon is running
Write-Info "Checking Docker daemon..."
try {
  docker info | Out-Null
  Write-Success "Docker daemon is running"
}
catch {
  Write-ErrorMsg "Docker daemon is not running!"
  Write-Host ""
  Write-Host "Please start Docker Desktop" -ForegroundColor Yellow
  exit 1
}

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptPath "..")

# Check for .env file
Write-Info "Checking environment configuration..."
if (-not (Test-Path ".env")) {
  Write-Warning ".env file not found"
  if (Test-Path "env.docker.example") {
    Write-Info "Copying env.docker.example to .env..."
    Copy-Item "env.docker.example" ".env"
    Write-Warning "Please update .env with your configuration before proceeding!"
    Write-Host ""
    Write-Host "Edit .env and update:" -ForegroundColor Yellow
    Write-Host "  - DB_PASSWORD" -ForegroundColor Yellow
    Write-Host "  - CRM_API_KEY (if using CRM integration)" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter after updating .env to continue, or Ctrl+C to cancel"
  }
  else {
    Write-ErrorMsg "env.docker.example not found!"
    exit 1
  }
}
Write-Success ".env file found"

# Build and run
Write-Host ""
Write-Info "Starting deployment..."
Write-Host ""

switch ($Action.ToLower()) {
  { ($_ -eq "up") -or ($_ -eq "start") } {
    Write-Info "Building and starting services..."
    if ($WithPgAdmin -eq "admin") {
      docker-compose --env-file .env --profile admin up --build -d
      Write-Success "Services started (including PgAdmin)"
      Write-Host ""
      Write-Host "Access PgAdmin at: http://localhost:5050" -ForegroundColor Cyan
      Write-Host "  Email: admin@jatan.com (change in .env)" -ForegroundColor Gray
      Write-Host "  Password: Check PGADMIN_PASSWORD in .env" -ForegroundColor Gray
    }
    else {
      docker-compose --env-file .env up --build -d
      Write-Success "Services started"
    }
  }

  { ($_ -eq "down") -or ($_ -eq "stop") } {
    Write-Info "Stopping services..."
    docker-compose down
    Write-Success "Services stopped"
  }

  "restart" {
    Write-Info "Restarting services..."
    docker-compose down
    docker-compose --env-file .env up --build -d
    Write-Success "Services restarted"
  }

  "logs" {
    Write-Info "Showing logs..."
    docker-compose logs -f
  }

  "clean" {
    Write-Warning "This will remove all containers, volumes, and data!"
    $response = Read-Host "Are you sure? (yes/no)"
    if ($response -eq "yes") {
      docker-compose down -v
      Write-Success "Cleaned up all containers and volumes"
    }
    else {
      Write-Info "Cleanup cancelled"
    }
  }

  "backup" {
    Write-Info "Creating database backup..."
    $backupFile = "backups/backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
    docker exec jatan_postgres pg_dump -U salary_admin labor_salary_db > $backupFile
    Write-Success "Backup created in ./backups/"
  }

  default {
    Write-Host "Usage: .\build_and_run.ps1 {up|down|restart|logs|clean|backup} [admin]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Cyan
    Write-Host "  up/start    - Build and start services"
    Write-Host "  down/stop   - Stop services"
    Write-Host "  restart     - Restart services"
    Write-Host "  logs        - Show container logs"
    Write-Host "  clean       - Remove all containers and volumes"
    Write-Host "  backup      - Create database backup"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  admin       - Also start PgAdmin for database management"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\build_and_run.ps1 up"
    Write-Host "  .\build_and_run.ps1 up admin"
    Write-Host "  .\build_and_run.ps1 logs"
    Write-Host "  .\build_and_run.ps1 backup"
    exit 1
  }
}

# Show container status
Write-Host ""
Write-Info "Container Status:"
docker ps --filter "name=jatan_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""
Write-Success "Deployment complete!"
Write-Host ""
Write-Host "Application URLs:" -ForegroundColor Cyan
Write-Host "  - PostgreSQL: localhost:5432"
Write-Host "  - Application: localhost:8000"
if ($WithPgAdmin -eq "admin") {
  Write-Host "  - PgAdmin: http://localhost:5050"
}
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  - View logs: docker-compose logs -f"
Write-Host "  - Stop: docker-compose down"
Write-Host "  - Access PostgreSQL: docker exec -it jatan_postgres psql -U salary_admin -d labor_salary_db"
Write-Host ""


