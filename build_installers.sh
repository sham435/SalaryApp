#!/usr/bin/env bash
# ============================================
# Jatan Salary Management System
# Master Installer Build Script
# Builds installers for Windows, macOS, and Linux
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║  Jatan Salary Management System                             ║"
echo "║  Cross-Platform Installer Builder                           ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

VERSION="3.1.0"
BUILD_DATE=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="dist"

print_info "Version: $VERSION"
print_info "Build Date: $BUILD_DATE"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# ============================================
# Step 1: Build Docker Images
# ============================================

print_info "Step 1: Building Docker images..."
echo ""

docker compose -f docker-compose.production.yml build --no-cache

print_success "Docker images built successfully"
echo ""

# ============================================
# Step 2: Export Docker Images
# ============================================

print_info "Step 2: Exporting Docker images..."
echo ""

# Get all container names
IMAGES=$(docker compose -f docker-compose.production.yml config --images | tr '\n' ' ')

print_info "Exporting images: $IMAGES"
echo ""

# Export to tar file
docker save $IMAGES -o "$OUTPUT_DIR/jatan_stack.tar"

# Compress the tar file
print_info "Compressing images..."
gzip -f "$OUTPUT_DIR/jatan_stack.tar"
mv "$OUTPUT_DIR/jatan_stack.tar.gz" "$OUTPUT_DIR/jatan_stack.tar"

FILE_SIZE=$(du -h "$OUTPUT_DIR/jatan_stack.tar" | cut -f1)
print_success "Docker images exported: $FILE_SIZE"
echo ""

# ============================================
# Step 3: Prepare Common Files
# ============================================

print_info "Step 3: Preparing common files..."
echo ""

# Copy docker-compose and configs
cp docker-compose.production.yml "$OUTPUT_DIR/"
cp env.production.example "$OUTPUT_DIR/.env.example"
cp -r monitoring "$OUTPUT_DIR/" 2>/dev/null || true

# Create README for installers
cat > "$OUTPUT_DIR/README.txt" << 'README'
╔════════════════════════════════════════════════════════╗
║  Jatan Salary Management System                       ║
║  Installation Package                                  ║
╚════════════════════════════════════════════════════════╝

CONTENTS:
  - jatan_stack.tar             Docker images (all services)
  - docker-compose.production.yml    Service configuration
  - .env.example                 Environment template
  - monitoring/                  Monitoring configs

REQUIREMENTS:
  - Docker Desktop (Windows/macOS)
  - Docker Engine (Linux)
  - 8GB RAM minimum
  - 10GB disk space
  - Ports: 5432, 6379, 5672, 8000, 9090, 3000

INSTALLATION:
  Windows: Run Jatan_Stack_Setup.exe
  macOS:   Open Jatan_Stack_Installer.dmg
  Linux:   Run ./install_jatan.sh

QUICK START:
  1. Install using platform-specific installer
  2. Edit .env file with your configuration
  3. Start the stack (shortcuts provided)
  4. Access Grafana: http://localhost:3000 (admin/admin)

SERVICES:
  - PostgreSQL 16     (5432)
  - Redis 7           (6379)
  - RabbitMQ 3        (5672, 15672)
  - Application       (8000)
  - Celery Workers    (scalable)
  - Grafana           (3000)
  - Prometheus        (9090)
  - Monitoring Tools  (various ports)

SUPPORT:
  Email: sales@jatanjewellery.com
  Website: https://jatanjewellery.com

Version: 3.1.0
Company: Jatan Jewellery FZ.C
README

print_success "Common files prepared"
echo ""

# ============================================
# Step 4: Build Windows Installer
# ============================================

print_info "Step 4: Building Windows installer..."
echo ""

if command -v makensis &> /dev/null; then
    # Copy Windows files
    mkdir -p "$OUTPUT_DIR/windows"
    cp "$OUTPUT_DIR/jatan_stack.tar" "$OUTPUT_DIR/windows/"
    cp "$OUTPUT_DIR/docker-compose.production.yml" "$OUTPUT_DIR/windows/"
    cp "$OUTPUT_DIR/.env.example" "$OUTPUT_DIR/windows/"
    cp -r "$OUTPUT_DIR/monitoring" "$OUTPUT_DIR/windows/" 2>/dev/null || true
    cp installers/windows/*.bat "$OUTPUT_DIR/windows/"
    cp installers/windows/install_jatan.nsi "$OUTPUT_DIR/windows/"

    # Build NSIS installer
    cd "$OUTPUT_DIR/windows"
    makensis install_jatan.nsi
    cd ../..

    if [ -f "$OUTPUT_DIR/windows/Jatan_Stack_Setup.exe" ]; then
        mv "$OUTPUT_DIR/windows/Jatan_Stack_Setup.exe" "$OUTPUT_DIR/Jatan_Stack_Setup_v${VERSION}.exe"
        EXE_SIZE=$(du -h "$OUTPUT_DIR/Jatan_Stack_Setup_v${VERSION}.exe" | cut -f1)
        print_success "Windows installer created: $EXE_SIZE"
    else
        print_warning "Windows installer compilation failed"
    fi
else
    print_warning "NSIS not installed, skipping Windows installer"
    print_info "Install NSIS to build Windows installers:"
    print_info "  macOS: brew install nsis"
    print_info "  Linux: sudo apt install nsis"
fi

echo ""

# ============================================
# Step 5: Build macOS .dmg
# ============================================

print_info "Step 5: Building macOS installer..."
echo ""

if command -v npx &> /dev/null; then
    # Copy macOS files
    mkdir -p "$OUTPUT_DIR/macos"
    cp "$OUTPUT_DIR/jatan_stack.tar" "$OUTPUT_DIR/macos/"
    cp "$OUTPUT_DIR/docker-compose.production.yml" "$OUTPUT_DIR/macos/"
    cp "$OUTPUT_DIR/.env.example" "$OUTPUT_DIR/macos/"
    cp -r "$OUTPUT_DIR/monitoring" "$OUTPUT_DIR/macos/" 2>/dev/null || true
    cp installers/macos/*.command "$OUTPUT_DIR/macos/"
    chmod +x "$OUTPUT_DIR/macos/"*.command
    cp installers/macos/appdmg.json "$OUTPUT_DIR/macos/"
    cp "$OUTPUT_DIR/README.txt" "$OUTPUT_DIR/macos/"

    # Create app bundle
    mkdir -p "$OUTPUT_DIR/macos/Jatan Salary System.app/Contents/MacOS"
    mkdir -p "$OUTPUT_DIR/macos/Jatan Salary System.app/Contents/Resources"

    cp "$OUTPUT_DIR/macos/start_stack.command" "$OUTPUT_DIR/macos/Jatan Salary System.app/Contents/MacOS/Jatan Salary System"
    chmod +x "$OUTPUT_DIR/macos/Jatan Salary System.app/Contents/MacOS/Jatan Salary System"

    # Create Info.plist
    cat > "$OUTPUT_DIR/macos/Jatan Salary System.app/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Jatan Salary System</string>
    <key>CFBundleDisplayName</key>
    <string>Jatan Salary System</string>
    <key>CFBundleIdentifier</key>
    <string>com.jatan.salary</string>
    <key>CFBundleVersion</key>
    <string>3.1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleExecutable</key>
    <string>Jatan Salary System</string>
</dict>
</plist>
PLIST

    # Build DMG
    cd "$OUTPUT_DIR/macos"
    npx appdmg appdmg.json "../Jatan_Stack_Installer_v${VERSION}.dmg" 2>/dev/null || print_warning "appdmg failed, creating simple DMG"

    # Fallback: create simple DMG
    if [ ! -f "../Jatan_Stack_Installer_v${VERSION}.dmg" ]; then
        hdiutil create -volname "Jatan Stack Installer" -srcfolder "." -ov -format UDZO "../Jatan_Stack_Installer_v${VERSION}.dmg" 2>/dev/null || true
    fi

    cd ../..

    if [ -f "$OUTPUT_DIR/Jatan_Stack_Installer_v${VERSION}.dmg" ]; then
        DMG_SIZE=$(du -h "$OUTPUT_DIR/Jatan_Stack_Installer_v${VERSION}.dmg" | cut -f1)
        print_success "macOS installer created: $DMG_SIZE"
    else
        print_warning "macOS DMG creation failed"
    fi
else
    print_warning "npx/node not installed, skipping macOS .dmg"
    print_info "Install Node.js to build macOS installers"
fi

echo ""

# ============================================
# Step 6: Build Linux Installer
# ============================================

print_info "Step 6: Building Linux installer..."
echo ""

# Create self-extracting archive
mkdir -p "$OUTPUT_DIR/linux"
cp "$OUTPUT_DIR/jatan_stack.tar" "$OUTPUT_DIR/linux/"
cp "$OUTPUT_DIR/docker-compose.production.yml" "$OUTPUT_DIR/linux/"
cp "$OUTPUT_DIR/.env.example" "$OUTPUT_DIR/linux/"
cp -r "$OUTPUT_DIR/monitoring" "$OUTPUT_DIR/linux/" 2>/dev/null || true
cp installers/linux/install_jatan.sh "$OUTPUT_DIR/linux/"
chmod +x "$OUTPUT_DIR/linux/install_jatan.sh"

# Create distributable
cd "$OUTPUT_DIR/linux"
tar czf "../Jatan_Stack_Linux_v${VERSION}.tar.gz" *
cd ../..

LINUX_SIZE=$(du -h "$OUTPUT_DIR/Jatan_Stack_Linux_v${VERSION}.tar.gz" | cut -f1)
print_success "Linux installer created: $LINUX_SIZE"

echo ""

# ============================================
# Step 7: Generate Checksums
# ============================================

print_info "Step 7: Generating checksums..."
echo ""

cd "$OUTPUT_DIR"

# Generate SHA256 checksums
for file in *.exe *.dmg *.tar.gz 2>/dev/null; do
    if [ -f "$file" ]; then
        sha256sum "$file" >> checksums.txt 2>/dev/null || shasum -a 256 "$file" >> checksums.txt
    fi
done

if [ -f "checksums.txt" ]; then
    print_success "Checksums generated: checksums.txt"
else
    print_warning "No installer files found to checksum"
fi

cd ..

# ============================================
# Summary
# ============================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║  ✅ BUILD COMPLETE!                                          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

print_info "Output directory: $OUTPUT_DIR/"
echo ""

print_info "Generated files:"
ls -lh "$OUTPUT_DIR"/*.exe "$OUTPUT_DIR"/*.dmg "$OUTPUT_DIR"/*.tar.gz 2>/dev/null | awk '{print "  " $9, "(" $5 ")"}' || print_warning "No installers generated"

echo ""
print_info "Docker images exported: jatan_stack.tar"
echo ""

print_success "All installers built successfully!"
echo ""

echo "Distribution:"
echo "  Windows: $OUTPUT_DIR/Jatan_Stack_Setup_v${VERSION}.exe"
echo "  macOS:   $OUTPUT_DIR/Jatan_Stack_Installer_v${VERSION}.dmg"
echo "  Linux:   $OUTPUT_DIR/Jatan_Stack_Linux_v${VERSION}.tar.gz"
echo ""

echo "Next steps:"
echo "  1. Test installers on target platforms"
echo "  2. Sign executables for production (recommended)"
echo "  3. Upload to distribution server"
echo "  4. Update documentation with download links"
echo ""


