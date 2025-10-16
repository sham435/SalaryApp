# 🍎 macOS Installation Guide
## Jatan Jewellery - Salary Management System

**Quick installation guide for macOS**

---

## ✅ Prerequisites

### 1. Install Docker Desktop for Mac

If you don't have Docker Desktop installed:

```bash
# Option 1: Using Homebrew (recommended)
brew install --cask docker

# Option 2: Manual download
# Visit: https://www.docker.com/products/docker-desktop
# Download and install Docker Desktop for Mac
```

After installation:
1. Open Docker Desktop from Applications
2. Wait for Docker to start (whale icon in menu bar)
3. Verify installation: `docker --version`

---

## 🚀 Installation Options

### **Option 1: Quick Start (Recommended)**

From the `installers/macos` directory:

```bash
# 1. Make scripts executable
chmod +x start_stack.command
chmod +x stop_stack.command

# 2. Start the application
./start_stack.command
```

**That's it!** The application will:
- Check Docker Desktop
- Load all Docker images
- Start all 16 services
- Open Grafana in your browser

### **Option 2: Full Installation (App Bundle)**

If you have the complete .dmg file:

```bash
# 1. Open the DMG
open Jatan_Stack_Installer_v3.2.0.dmg

# 2. Drag "Jatan Salary System" to Applications folder

# 3. Launch from Applications or Spotlight
open "/Applications/Jatan Salary System.app"
```

### **Option 3: Manual Installation**

```bash
# 1. Navigate to project root
cd "/Users/sham4/my all app proj/Jatan_All_Projects/SalaryApp"

# 2. Copy environment file
cp env.production.example .env
nano .env  # Update passwords if needed

# 3. Start the full stack
./scripts/build_production.sh up monitoring admin

# Wait a few minutes for all services to start

# 4. Access Grafana
open http://localhost:3000
```

---

## 📊 Access Your Application

After installation, access these URLs:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana Dashboard** | http://localhost:3000 | admin/admin |
| **Application** | http://localhost:8000 | - |
| **RabbitMQ Management** | http://localhost:15672 | admin/admin123 |
| **Flower (Celery)** | http://localhost:5555 | - |
| **PgAdmin (Database)** | http://localhost:5050 | admin@jatan.com/admin123 |
| **Prometheus** | http://localhost:9090 | - |

---

## 🎨 First Time Setup

### 1. Access Grafana
```bash
open http://localhost:3000
```
- Login: `admin` / `admin`
- Change password on first login (recommended)

### 2. Import Dashboards
1. Click **+** → **Import**
2. Enter these dashboard IDs:
   - **9628** - PostgreSQL Performance
   - **763** - Redis Metrics
   - **10991** - RabbitMQ Monitoring
   - **12856** - Celery Tasks
   - **193** - Docker Containers
   - **1860** - System Overview

3. Select "Prometheus" as datasource
4. Click **Import**

### 3. Start Using the Application
- Access the main app at http://localhost:8000
- Or use the SQLite version: `python salary_calculator_gui.py`

---

## 🛠️ Common Commands

### Start the Stack
```bash
cd installers/macos
./start_stack.command
```

### Stop the Stack
```bash
cd installers/macos
./stop_stack.command
```

### Check Status
```bash
docker ps
```

### View Logs
```bash
docker compose -f docker-compose.production.yml logs -f
```

### Restart Services
```bash
docker compose -f docker-compose.production.yml restart
```

---

## 🐛 Troubleshooting

### Docker Desktop Not Running

**Problem**: "Cannot connect to Docker daemon"

**Solution**:
```bash
# Start Docker Desktop
open -a Docker

# Wait for Docker to fully start (whale icon in menu bar)
# Then try again
```

### Port Already in Use

**Problem**: "Port 5432 is already allocated"

**Solution**:
```bash
# Check what's using the port
lsof -i :5432

# Kill the process or change port in .env
nano .env
# Change DB_PORT=5433
```

### Permission Denied

**Problem**: "Permission denied" when running scripts

**Solution**:
```bash
# Make scripts executable
chmod +x start_stack.command
chmod +x stop_stack.command
```

### Application Not Opening

**Problem**: Grafana doesn't open in browser

**Solution**:
```bash
# Manually open
open http://localhost:3000

# Or check if services are running
docker ps | grep jatan
```

### Reset Everything

**Problem**: Need to start fresh

**Solution**:
```bash
# Stop and remove all containers and volumes
docker compose -f docker-compose.production.yml down -v

# Remove images (optional)
docker rmi $(docker images | grep jatan | awk '{print $3}')

# Start again
./start_stack.command
```

---

## 📱 Alternative: Use Built-in SQLite Version

If you prefer a simpler option without Docker:

```bash
# Navigate to project root
cd "/Users/sham4/my all app proj/Jatan_All_Projects/SalaryApp"

# Activate virtual environment
source ~/.virtualenvs/global/bin/activate
# Or if using the custom command:
gvenv_on

# Run the application
python salary_calculator_gui.py
```

This gives you all features except:
- Multi-user support
- Async CRM synchronization
- Advanced monitoring
- Horizontal scaling

---

## 🔧 Advanced Options

### Run in Background
```bash
# Start without opening terminal window
nohup ./start_stack.command > /dev/null 2>&1 &
```

### Auto-Start on Login
```bash
# Add to Login Items
osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Applications/Jatan Salary System.app", hidden:false}'
```

### Check Resource Usage
```bash
# Monitor Docker containers
docker stats

# Check disk usage
docker system df
```

---

## 📚 Documentation

For more details, see:
- **ULTIMATE_GUIDE.md** - Complete guide
- **README_MASTER.md** - Main documentation
- **QUICK_START.md** - 5-minute setup
- **MONITORING_GUIDE.md** - Monitoring setup

---

## 📞 Support

### Need Help?

1. **Check logs**:
   ```bash
   tail -f ~/jatan_stack/logs/salary_app.log
   docker compose logs -f
   ```

2. **Verify Docker**:
   ```bash
   docker ps
   docker info
   ```

3. **Contact Support**:
   - Email: sales@jatanjewellery.com
   - Website: https://jatanjewellery.com

---

## ✅ Quick Reference

```bash
# Start
./start_stack.command

# Stop
./stop_stack.command

# Status
docker ps | grep jatan

# Logs
docker compose logs -f

# Access
open http://localhost:3000
```

---

**Version**: 3.2.0
**Platform**: macOS 10.15+
**Status**: ✅ Ready to Use

🎉 **Enjoy your new salary management system!** 🚀


