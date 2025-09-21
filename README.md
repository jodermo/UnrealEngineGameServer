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

### Common Build Issues

#### Missing ISPC Headers
```bash
# Error: 'GeometryCollectionSceneProxy.ispc.generated.h' file not found
# Solution: Install ISPC (see Step 3 above)
```

#### Missing Dependencies
```bash
sudo apt-get install -y \
    libglib2.0-0 libsm6 libice6 libxcomposite1 \
    libxrender1 libfontconfig1 libxss1 libxtst6 libxi6
```

#### Build Cache Issues
```bash
# Clean everything and rebuild
cd ~/UnrealProjects/YourProjectName
rm -rf Binaries/ Intermediate/ DerivedDataCache/ Saved/
./Scripts/clean_build.sh
docker-compose down
docker-compose up --build
```

#### ISPC Build Problems
```bash
# Disable ISPC if causing issues
export UE_BUILD_DISABLE_ISPC=1
./Scripts/build.sh full
```

### Container Issues

#### Server Not Starting
```bash
# Check logs
docker-compose logs ue-game-server

# Check if binary exists
docker-compose exec ue-game-server ls -la ./LinuxServer/
```

#### Database Connection Issues
```bash
# Restart database service
docker-compose restart ue-database

# Check database health
docker-compose exec ue-database pg_isready -U admin -d uegame
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