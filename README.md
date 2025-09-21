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

## Project Structure

```
~/UnrealEngineGameServer/          # This repository
├── .env                           # Environment configuration
├── docker-compose.yml             # Service orchestration
├── Dockerfile                     # Server container image
├── GameServer.sh                  # Server startup script
├── README.md                      # This file
├── DjangoBackend/                 # Django REST API
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── config/
├── Scripts/                       # Build automation
│   ├── build.sh
│   ├── clean_build.sh
│   ├── gen_server_target.sh
│   └── copy_project_files.sh
├── UnrealProjects/                # Source code and builds
│   ├── UnrealEngine/              # Engine source
│   └── YourProjectName/           # Your game project
│       ├── Build/LinuxServer/     # Packaged server build
│       ├── Binaries/
│       ├── Content/
│       ├── Config/
│       ├── Source/
│       └── YourProjectName.uproject
├── logs/                          # Runtime logs
│   ├── server/
│   ├── crashes/
│   └── abs/
└── backups/                       # Database backups
```

## Quick Start

### 1. Environment Configuration

Create a `.env` file in the project root:

```env
# Unreal Server Settings
PROJECT_NAME=EvolutionGame
UE_PORT=7777
UE_QUERY_PORT=27015
UE_MAP=/Game/EvolutionGame/Levels/LobbyMap
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
PROJECT_DIR=UnrealProjects/EvolutionGame
BINARIES_DIR=UnrealProjects/EvolutionGame/Binaries
BUILD_DIR=UnrealProjects/EvolutionGame/Build

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
mkdir -p ~/UnrealProjects/YourProjectName
# Copy your Windows project files here or clone from repository

# Make build scripts executable
chmod +x Scripts/*.sh
```

### Step 5: Generate Server Target (If Not Exists)

```bash
./Scripts/gen_server_target.sh
```

This creates `YourProjectNameServer.Target.cs`:

```csharp
using UnrealBuildTool;
using System.Collections.Generic;

public class YourProjectNameServerTarget : TargetRules
{
    public YourProjectNameServerTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Server;
        DefaultBuildSettings = BuildSettingsVersion.V2;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_6;
        ExtraModuleNames.Add("YourProjectName");
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
ls -la Source/YourProjectNameServer.Target.cs
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
cd ~/UnrealProjects/YourProjectName
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
docker-compose exec ue-game-server file ./LinuxServer/YourProject/Binaries/Linux/YourProjectServer-Linux-Shipping

# Test binary dependencies
docker-compose exec ue-game-server ldd ./LinuxServer/YourProject/Binaries/Linux/YourProjectServer-Linux-Shipping
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
docker-compose exec ue-game-server gdb ./LinuxServer/YourProject/Binaries/Linux/YourProjectServer-Linux-Development
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
ldd ./LinuxServer/YourProject/Binaries/Linux/YourProjectServer-Linux-Shipping

# Verify binary architecture
file ./LinuxServer/YourProject/Binaries/Linux/YourProjectServer-Linux-Shipping

# Check for symbols
nm ./LinuxServer/YourProject/Binaries/Linux/YourProjectServer-Linux-Shipping | head
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
UE_MAP=/Game/YourProject/Levels/YourMap
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