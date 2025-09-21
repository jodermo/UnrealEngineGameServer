# Unreal Engine Dedicated Server (Dockerized)

**Author:** [Moritz Petzka](https://github.com/jodermo) • [petzka.com](https://petzka.com) • [info@petzka.com](mailto:info@petzka.com)

A complete solution for running an Unreal Engine dedicated Linux server as a Docker container with included Django backend and PostgreSQL database for admin tools and dynamic REST API.

## Features

- Headless Unreal Engine dedicated server
- Docker and Docker Compose support
- Persistent volumes for saved data/logs
- Configurable map, port, and logging settings
- PostgreSQL database with Django REST API
- Admin interface for server management
- Minimal base image (Ubuntu 22.04)
- Automated build scripts for different scenarios

## Prerequisites

- Docker and Docker Compose
- Access to [Unreal Engine GitHub repository](https://www.unrealengine.com/en-US/ue-on-github)
- Linux or WSL with required build tools
- Unreal Engine 5.6+ (recommended)
- Minimum 32GB RAM, 200GB+ free disk space
- Multi-core CPU (8+ cores recommended)

## Project Structure

```
UnrealEngineGameServer/            # This repository
    .env                           # Environment configuration
    docker-compose.yml             # Service orchestration
    Dockerfile                     # Server container image
    GameServer.sh                  # Server startup script
    DjangoBackend/                 # Django REST API
        Dockerfile                 # Django container image
        entrypoint.sh              # Django startup script
        config/                    # Django configuration
    Scripts/                       # Build automation scripts
        build.sh                   # Main build script
        check_build.sh             # Build verification
        clear_all.sh               # Clear all builds
        clear_build.sh             # Clear build cache
        clear_engine.sh            # Clear engine cache
        debug_server.sh            # Debug server script
        gen_server_target.sh       # Generate server target
        startup.sh                 # Startup script
    UnrealProjects/                # Source code and builds
        UnrealEngine/              # Engine source code
        <ProjectName>/             # Your game project
            Binaries/              # Compiled binaries
            Build/                 # Build output directory
            Config/                # Project configuration
            Content/               # Game content assets
            Source/                # C++ source code
            <ProjectName>.uproject # Project file
    logs/                          # Runtime and build logs
        abs/                       # Absolute logs
        crashes/                   # Crash reports
        logs/                      # General logs
        server/                    # Server logs
        ue/                        # Unreal Engine logs
    backups/                       # Database backups
```

## Quick Start

### 1. Environment Configuration

Create a `.env` file in the project root:

```env
# Unreal Server Settings
PROJECT_NAME=<ProjectName>
UE_PORT=7777
UE_QUERY_PORT=27015
UE_DEBUG=1
UE_LOGGING=1

# Database Configuration
DB_NAME=uegame
DB_USER=admin
DB_PASSWORD=securepassword

# Django Admin (Optional)
CREATE_SUPERUSER=1
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123

# Build Configuration
UNREAL_VERSION=5_6
BUILD_CONFIG=Shipping
UNREAL_ENGINE_PATH=UnrealProjects/UnrealEngine
PROJECT_DIR=UnrealProjects/<ProjectName>
BINARIES_DIR=UnrealProjects/<ProjectName>/Binaries
BUILD_DIR=UnrealProjects/<ProjectName>/Build
UE_MAPS=/Game/Levels/StartMap,/Game/Levels/FirstLevel # all cooked maps
UE_MAP=/Game/Levels/StartMap # default start map

# Build Optimization
UBT_NO_UBT_BUILD_ACCELERATOR=1
UE_BUILD_DISABLE_ISPC=1
```

### 2. Build and Run

```bash
# Build the containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access Services

- **Game Server**: UDP port 7777 (configurable)
- **Django Admin**: http://localhost:8000/admin
- **REST API**: http://localhost:8000/api/
- **PostgreSQL**: localhost:5432

## Complete Setup Guide

### Step 0: Initial Linux Environment Setup

Before beginning with Unreal Engine, ensure your Linux system is properly configured with all required dependencies and tools.

#### System Requirements Check
```bash
# Check available disk space (need 200GB+ free)
df -h

# Check RAM (32GB+ recommended)
free -h

# Check CPU cores (8+ recommended)
nproc

# Check Linux distribution and version
lsb_release -a
```

#### Update System and Install Base Dependencies
```bash
# Update package lists and upgrade system
sudo apt update && sudo apt upgrade -y

# Install essential development tools
sudo apt install -y \
    curl wget git vim nano \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install build essentials
sudo apt install -y \
    build-essential \
    clang \
    lld \
    cmake \
    make \
    ninja-build \
    pkg-config
```

#### Install Unreal Engine Specific Dependencies
```bash
# Install required libraries for UE compilation
sudo apt install -y \
    libncurses5-dev \
    libssl-dev \
    libx11-dev \
    libxcursor-dev \
    libxinerama-dev \
    libxrandr-dev \
    libxi-dev \
    libglib2.0-dev \
    libpulse-dev \
    libsdl2-dev \
    libfontconfig1-dev \
    libfreetype6-dev \
    libgtk-3-dev \
    libasound2-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libvorbis-dev \
    libogg-dev \
    libtheora-dev \
    libvpx-dev \
    libxss1 \
    libgconf-2-4

# Install additional runtime libraries
sudo apt install -y \
    libglib2.0-0 \
    libsm6 \
    libice6 \
    libxcomposite1 \
    libxrender1 \
    libfontconfig1 \
    libxtst6 \
    libxi6 \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    libasound2
```

#### Install Mono (Required for UE Build Tools)
```bash
# Add Mono repository
sudo apt install -y dirmngr gnupg apt-transport-https ca-certificates
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
echo "deb https://download.mono-project.com/repo/ubuntu stable-focal main" | sudo tee /etc/apt/sources.list.d/mono-official-stable.list

# Update and install Mono
sudo apt update
sudo apt install -y mono-devel mono-complete

# Verify Mono installation
mono --version
```

#### Install Docker and Docker Compose
```bash
# Remove old Docker versions if they exist
sudo apt remove -y docker docker-engine docker.io containerd runc

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add current user to docker group (avoid using sudo with docker)
sudo usermod -aG docker $USER

# Verify Docker installation
docker --version
docker compose version

# Test Docker (run this after logging out and back in)
docker run hello-world
```

#### Install Additional Build Tools
```bash
# Install Python (needed for some UE scripts)
sudo apt install -y python3 python3-pip python3-dev

# Install Node.js (for potential web interfaces)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# Install additional utilities
sudo apt install -y \
    dos2unix \
    unzip \
    p7zip-full \
    tree \
    htop \
    screen \
    tmux \
    netcat-openbsd
```

#### Configure Git (Required for UE Repository Access)
```bash
# Configure Git with your credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Generate SSH key for GitHub (if using SSH)
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add SSH key to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Display public key to add to GitHub
cat ~/.ssh/id_ed25519.pub
```

#### Setup Epic Games GitHub Access
Before proceeding, you must link your Epic Games account to GitHub:

1. **Link Accounts**: Visit your [Epic Games account page](https://www.epicgames.com/account/connected)
2. **Connect GitHub**: Find the "Connections" tab and link your GitHub account
3. **Join Organization**: Check your email for an invitation to join the Epic Games GitHub organization
4. **Accept Invitation**: Accept the invitation to gain access to the UnrealEngine repository

#### Test GitHub Access
```bash
# Test SSH access to GitHub (if using SSH)
ssh -T git@github.com

# Test HTTPS access (if using HTTPS)
git ls-remote https://github.com/EpicGames/UnrealEngine.git

# You should see repository information if access is working
```

#### Create Project Directory Structure
```bash
# Create main project directory
mkdir -p ~/UnrealEngineGameServer
cd ~/UnrealEngineGameServer

# Create subdirectories
mkdir -p {logs/{server,crashes,abs,ue},backups,Scripts,DjangoBackend,UnrealProjects}

# Set proper permissions
chmod 755 ~/UnrealEngineGameServer
```

#### System Optimization for Large Builds
```bash
# Increase file descriptor limits for large builds
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Increase virtual memory for linking
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf

# Increase swap if you have less than 32GB RAM
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Apply sysctl changes
sudo sysctl -p
```

#### Verify Installation
```bash
# Create a verification script
cat << 'EOF' > ~/verify_setup.sh
#!/bin/bash
echo "=== System Verification ==="
echo "OS: $(lsb_release -d | cut -f2)"
echo "Kernel: $(uname -r)"
echo "CPU Cores: $(nproc)"
echo "RAM: $(free -h | grep Mem: | awk '{print $2}')"
echo "Disk Space: $(df -h ~ | tail -1 | awk '{print $4}') available"
echo ""
echo "=== Tool Versions ==="
echo "GCC: $(gcc --version | head -1)"
echo "Clang: $(clang --version | head -1)"
echo "CMake: $(cmake --version | head -1)"
echo "Git: $(git --version)"
echo "Docker: $(docker --version)"
echo "Mono: $(mono --version | head -1)"
echo ""
echo "=== GitHub Access ==="
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "GitHub SSH: ✓ Working"
else
    echo "GitHub SSH: ✗ Not configured or not working"
fi
echo ""
echo "=== Directory Structure ==="
tree ~/UnrealEngineGameServer -L 2 2>/dev/null || ls -la ~/UnrealEngineGameServer
EOF

chmod +x ~/verify_setup.sh
~/verify_setup.sh
```

**Important Notes:**
- Log out and log back in after adding yourself to the docker group
- Ensure you have accepted the Epic Games GitHub organization invitation
- The initial Unreal Engine build will take 4-8 hours depending on your hardware
- Monitor disk space during builds as they can consume 100GB+ temporarily

### Step 1: Install Prerequisites (Linux/WSL)

```bash
sudo apt update
sudo apt install -y \
    clang lld cmake make git build-essential \
    libncurses5 libssl-dev libx11-dev libxcursor-dev \
    libxinerama-dev libxrandr-dev libxi-dev \
    libglib2.0-dev libpulse-dev libsdl2-dev \
    mono-devel dos2unix unzip wget
```

### Step 2: Install Unreal Engine

**Note**: Requires [GitHub access to Epic Games repository](https://www.unrealengine.com/en-US/ue-on-github)

```bash
# Create project directory
mkdir -p ~/UnrealProjects
cd ~/UnrealProjects

# Clone Unreal Engine (choose one method)
# Method A: SSH
git clone --depth=1 -b 5.6 git@github.com:EpicGames/UnrealEngine.git

# Method B: HTTPS
git clone --depth=1 -b 5.6 https://github.com/EpicGames/UnrealEngine.git

# Build Unreal Engine (this takes a long time!)
cd UnrealEngine
./Setup.sh
./GenerateProjectFiles.sh
make
```

### Step 3: Install ISPC (Required for UE 5.6)

```bash
# Download and install ISPC
cd ~/Downloads
wget https://github.com/ispc/ispc/releases/download/v1.21.0/ispc-v1.21.0-linux.tar.gz
tar -xvzf ispc-v1.21.0-linux.tar.gz
cd ispc-v1.21.0-linux

# Install globally
sudo cp bin/ispc /usr/local/bin/
chmod +x /usr/local/bin/ispc

# Verify installation
ispc --version
```

### Step 4: Prepare Your Game Project

```bash
# Copy your project to the UnrealProjects directory
mkdir -p ~/UnrealProjects/<ProjectName>
# Copy your Windows project files here or clone from repository

# Make build scripts executable
chmod +x Scripts/*.sh
```

### Step 5: Generate Server Target (If Not Exists)

```bash
./Scripts/gen_server_target.sh
```

This creates `<ProjectName>Server.Target.cs`:

```csharp
using UnrealBuildTool;
using System.Collections.Generic;

public class <ProjectName>ServerTarget : TargetRules
{
    public <ProjectName>ServerTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Server;
        DefaultBuildSettings = BuildSettingsVersion.V2;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_6;
        ExtraModuleNames.Add("<ProjectName>");
    }
}
```

## Build Scripts Usage

The included build scripts provide different build modes for various scenarios:

```bash
# Rebuild C++ code only (fastest)
./Scripts/build.sh code

# Blueprint changes only
./Scripts/build.sh blueprints

# Content-only changes (textures, meshes, etc.)
./Scripts/build.sh content

# Server binaries only
./Scripts/build.sh server

# Full package (default - everything)
./Scripts/build.sh full

# Clean build (removes all cached files)
./Scripts/clean_build.sh
```

### Build Modes Comparison

| Mode         | Description                   | Cook | Build | Pak | Archive | Speed    |
|--------------|-------------------------------|------|-------|-----|---------|----------|
| `code`       | C++ only, no content changes | -    | X     | -   | -       | Fastest  |
| `blueprints` | Blueprint changes only        | X    | -     | X   | -       | Fast     |
| `content`    | Content-only changes          | X    | -     | X   | -       | Medium   |
| `server`     | Server binaries only          | -    | X     | -   | -       | Fast     |
| `full`       | Complete cook + pak + archive | X    | X     | X   | X       | Slowest  |

## Django Backend Configuration

The Django backend provides a REST API for game data management and admin interface.

### Dynamic Entity Generation

Configure your game entities in `DjangoBackend/config/entities.json`:

```json
{
    "Player": {
        "fields": {
            "username": "CharField(max_length=50, unique=True)",
            "email": "EmailField()",
            "score": "IntegerField(default=0)",
            "is_active": "BooleanField(default=True)"
        }
    },
    "Match": {
        "fields": {
            "match_id": "CharField(max_length=32, unique=True)",
            "start_time": "DateTimeField()",
            "end_time": "DateTimeField(null=True, blank=True)",
            "winner": "ForeignKey('Player', on_delete=models.DO_NOTHING, null=True)"
        }
    }
}
```

The system automatically generates:
- Django models
- REST API endpoints
- Admin interface
- Database migrations

## Troubleshooting

### ISPC (Intel Implicit SPMD Program Compiler) Issues

**The most common build issue in UE 5.5+ is ISPC-related errors. Here are the solutions:**

#### Method 1: Disable ISPC in Build Configuration (Recommended)
For persistent ISPC errors during engine builds, disable ISPC compilation by editing the build configuration file:

```bash
# Edit the Linux build configuration
nano ~/UnrealProjects/UnrealEngine/Engine/Source/Programs/UnrealBuildTool/Platform/Linux/UEBuildLinux.cs

# Around line 273, change:
Target.bCompileISPC = true;
# to:
Target.bCompileISPC = false;
```

#### Method 2: Install Compatible ISPC Version
```bash
# Download ISPC 1.21.0 (LLVM 15.x compatible with UE 5.6)
cd ~/Downloads
wget https://github.com/ispc/ispc/releases/download/v1.21.0/ispc-v1.21.0-linux.tar.gz
tar -xvzf ispc-v1.21.0-linux.tar.gz
cd ispc-v1.21.0-linux

# Install globally
sudo cp bin/ispc /usr/local/bin/
chmod +x /usr/local/bin/ispc

# Verify installation
ispc --version
```

#### Method 3: Environment Variable Override
```bash
# Disable ISPC via environment variable
export UE_BUILD_DISABLE_ISPC=1
./Scripts/build.sh full
```

### Docker Memory and Storage Issues

#### Container Memory Exhaustion
Docker containers don't enforce memory limits by default, which can cause them to consume all available system memory. Add memory limits to your `docker-compose.yml`:

```yaml
services:
  ue-game-server:
    # ... other configuration
    mem_limit: 8g  # Adjust based on your system
    memswap_limit: 8g
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G
```

#### Zen Server Storage Issues
For "insufficient storage" errors from Zen server, modify the cache location:

```bash
# Edit BaseEngine.ini in your Unreal Engine installation
nano ~/UnrealProjects/UnrealEngine/Engine/Config/BaseEngine.ini

# Find [Zen.AutoLaunch] section and change:
DataPath=%ENGINEVERSIONAGNOSTICINSTALLEDUSERDIR%Zen/Data
# to:
DataPath=%GAMEDIR%/Saved/ZenCache
```

#### Docker Desktop Storage Limits
Increase Docker's maximum container disk size to accommodate large Unreal Engine builds:

```json
// Edit Docker daemon.json (usually in ~/.docker/daemon.json)
{
  "storage-opts": [
    "size=300G"
  ]
}
```

### Common Build Issues

#### Missing Dependencies
```bash
sudo apt-get update && sudo apt-get install -y \
    libglib2.0-0 libsm6 libice6 libxcomposite1 \
    libxrender1 libfontconfig1 libxss1 libxtst6 libxi6 \
    libncurses5 libssl-dev libx11-dev libxcursor-dev \
    libxinerama-dev libxrandr-dev libxi-dev \
    libglib2.0-dev libpulse-dev libsdl2-dev
```

#### UE4Server Target Not Found
If you get "Couldn't find target rules file for target 'UE4Server'" error, ensure your server target file exists:

```bash
# Generate server target if missing
./Scripts/gen_server_target.sh

# Verify the server target file exists
ls -la Source/<ProjectName>Server.Target.cs
```

#### Vulkan/Graphics Driver Issues
For VulkanRHI crashes in containers, use software rendering:

```bash
# Add to your GameServer.sh or container startup
-opengl  # Force OpenGL instead of Vulkan
-nullrhi # Use null rendering (no graphics output)
```

### Build Cache Issues

#### Complete Clean Build
```bash
# Clean everything and rebuild
cd ~/UnrealProjects/<ProjectName>
rm -rf Binaries/ Intermediate/ DerivedDataCache/ Saved/

# Clean Unreal Engine build cache
cd ~/UnrealProjects/UnrealEngine
rm -rf Engine/Intermediate Engine/Binaries/Linux

# Rebuild from scratch
./Scripts/clean_build.sh
docker-compose down -v
docker-compose up --build
```

#### Incremental Build Issues
```bash
# For faster incremental builds, only clean project-specific files
rm -rf Binaries/ Intermediate/
# Keep DerivedDataCache/ and Saved/ for faster subsequent builds
```

### Container Runtime Issues

#### Server Not Starting
```bash
# Check detailed logs
docker-compose logs -f ue-game-server

# Check if binary exists and is executable
docker-compose exec ue-game-server ls -la ./LinuxServer/
docker-compose exec ue-game-server file ./LinuxServer/<ProjectName>/Binaries/Linux/<ProjectName>Server-Linux-Shipping

# Test binary dependencies
docker-compose exec ue-game-server ldd ./LinuxServer/<ProjectName>/Binaries/Linux/<ProjectName>Server-Linux-Shipping
```

#### Permission Issues
```bash
# Fix ownership issues
sudo chown -R 1000:1000 UnrealProjects/
sudo chown -R 1000:1000 logs/

# Ensure scripts are executable
chmod +x Scripts/*.sh
chmod +x GameServer.sh
```

#### Network/Port Issues
```bash
# Check if ports are accessible
docker-compose exec ue-game-server netstat -tulpn
docker-compose exec ue-game-server nc -z -u 127.0.0.1 7777

# Test from host
nc -z -u localhost 7777
```

### Database Issues

#### Connection Problems
```bash
# Check database health
docker-compose exec ue-database pg_isready -U admin -d uegame

# View database logs
docker-compose logs ue-database

# Connect manually to test
docker-compose exec ue-database psql -U admin -d uegame
```

#### Django Migration Issues
```bash
# Reset Django database
docker-compose exec ue-django-backend python manage.py migrate --fake-initial
docker-compose exec ue-django-backend python manage.py migrate
```

### Performance Optimization

#### WSL2 Memory Management
If using WSL2, create `~/.wslconfig` to limit resource usage:

```ini
[wsl2]
memory=8GB
processors=4
```

#### Build Performance
```bash
# Use multiple cores for faster builds
export MAKEFLAGS="-j$(nproc)"

# Reduce memory usage during builds
export UBT_PARALLEL_EXECUTOR=false
```

### Debugging Tips

#### Enable Debug Mode
```bash
# Set debug environment variables
UE_DEBUG=1
UE_LOGGING=1
BUILD_CONFIG=Development

# Run with GDB for crash analysis
docker-compose exec ue-game-server gdb ./LinuxServer/<ProjectName>/Binaries/Linux/<ProjectName>Server-Linux-Development
```

#### Monitor Resource Usage
```bash
# Monitor container resources
docker stats

# Check disk usage
docker system df
docker system prune -a  # Clean unused resources
```

#### Binary Analysis
```bash
# Check binary dependencies
ldd ./LinuxServer/<ProjectName>/Binaries/Linux/<ProjectName>Server-Linux-Shipping

# Verify binary architecture
file ./LinuxServer/<ProjectName>/Binaries/Linux/<ProjectName>Server-Linux-Shipping

# Check for symbols
nm ./LinuxServer/<ProjectName>/Binaries/Linux/<ProjectName>Server-Linux-Shipping | head
```

### Performance Optimization

#### For Development
```bash
# Use development build for faster iteration
BUILD_CONFIG=Development docker-compose up --build
```

#### For Production
```bash
# Use shipping build for optimal performance
BUILD_CONFIG=Shipping docker-compose up --build
```

## Maintenance Commands

```bash
# View real-time logs
docker-compose logs -f

# Restart specific service
docker-compose restart ue-game-server

# Update containers
docker-compose pull
docker-compose up -d

# Backup database
docker-compose exec ue-database pg_dump -U admin uegame > backup.sql

# Clean up unused containers/images
docker system prune -a
```

## Advanced Configuration

### Custom Game Maps
Update `.env` to change the default map:
```env
UE_MAP=/Game/Levels/YourMap
```

### Port Configuration
```env
UE_PORT=7777          # Game port
UE_QUERY_PORT=27015   # Query port
```

### Logging Configuration
```env
UE_LOGGING=1          # Enable file logging
UE_DEBUG=1            # Enable debug mode with GDB
```

## Security Considerations

- Change default database passwords in production
- Use environment-specific `.env` files
- Consider firewall rules for exposed ports
- Regularly update base images and dependencies
- Monitor logs for suspicious activity

## Support

For issues and questions:
- Check the troubleshooting section above
- Review Docker and Unreal Engine logs
- Ensure all prerequisites are installed
- Verify your Unreal Engine GitHub access

## License

This project is provided as-is for educational and development purposes. Unreal Engine usage is subject to Epic Games' licensing terms.