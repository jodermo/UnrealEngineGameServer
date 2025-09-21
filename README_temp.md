# Unreal Engine Dedicated Server (Dockerized)

**Author:** [Moritz Petzka](https://github.com/jodermo) • [petzka.com](https://petzka.com) • [info@petzka.com](mailto:info@petzka.com)

#### Unreal Engine dedicated Linux server as Docker container with included Django backend and database for admin tools and dynamic REST-API

### Features

- Headless Unreal Engine dedicated server
- Docker and Docker Compose support
- Persistent volume for saved data/logs
- Configurable map, port, and logging
- Minimal base image (Ubuntu 22.04)

### Prerequisites

- Docker and Docker Compose
- Access to Unreal Engine GitHub repository
- Linux or WSL with required build tools



### .env Example

```env
# Unreal server
PROJECT_NAME=YourProjectName
UE_PORT=7777
UE_MAP=LobbyMap
UE_LOGGING=1

# Database settings
DB_NAME=uegame
DB_USER=admin
DB_PASSWORD=securepassword

# Optional: superuser for Django admin
CREATE_SUPERUSER=1
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123


# UnrealEngine Build
UNREAL_VERSION=5_6
BUILD_CONFIG=Shipping
PROJECT_DIR=UnrealProjects/YourProjectName
ARCHIVE_DIR=Packaged/YourProjectName
UNREAL_ENGINE_PATH=UnrealProjects/UnrealEngine
```

## Getting Started

### 1. Package the Server

Use Unreal Editor or automation tools to package your project as a **Linux dedicated server**, then place the output in the `GameServer/` folder.

### 2. Build the Docker Image

```bash
docker-compose build
```

### 3. Run the Server

```bash
docker-compose up -d
```
This will expose the server on port 7777 (UDP) and 15000 (TCP by default).

## Cleanup

```bash
docker-compose down
```

To remove containers, networks, and volumes (careful with Saved/ data):

```bash
docker-compose down -v
```



<br>

## Guide To Package Your Unreal Engine Project For Linux Server

File structure overview:

```bash
~/UnrealEngineGameServer/   # This respoitory
├── Saved/
├── logs/
├── UnrealProjects/         # Contains source code for project build
│   ├── UnrealEngine/                  
│   │   └── ...                      
│   ├── YourProjectName/                
│   │   ├── Binaries/
│   │   ├── Content/
│   │   ├── Config/
│   │   ├── Source/
│   │   └── YourProjectName.uproject

```

### 1. Install Prerequisites

#### In Linux (or use [subsystem on windows](https://learn.microsoft.com/en-us/windows/wsl/install)), run:

```bash
sudo apt update
sudo apt install clang lld cmake make git build-essential libncurses5 libssl-dev libx11-dev \
    libxcursor-dev libxinerama-dev libxrandr-dev libxi-dev libglib2.0-dev libpulse-dev \
    libsdl2-dev mono-devel dos2unix unzip
```

### 2. Install UnrealEngine*

****([GitHub access to offical UnrealEngine repository](https://www.unrealengine.com/en-US/ue-on-github) needed )***

```bash
mkdir -p ~/UnrealProjects
cd ~/UnrealProjects
```

- Option A: Clone UnrealEngine via SSH
    ```bash
    git clone --depth=1 -b 5.6 git@github.com:EpicGames/UnrealEngine.git
    ```

- Option B: Clone UnrealEngine via HTTP
    ```bash
    git clone --depth=1 -b 5.6 https://github.com/EpicGames/UnrealEngine.git
    ```

### 3. Run Setup & Generate Project Files

```bash
cd ~/UnrealProjects/UnrealEngine
./Setup.sh
./GenerateProjectFiles.sh
make
```
This builds the Unreal Engine Linux version in WSL. It will take a long time.

### 4. Build Your Game's Linux Server

```bash
mkdir -p ~/UnrealProjects/YourProjectName
```
Copy your Windows project into this directory or clone from a repo

### Build Scripts

Calling engine build with the build accelerator disabled:
```
Engine/Build/BatchFiles/RunUBT.sh -NoUBTBuildAccelerator EpicWebHelper Linux Shipping

Engine/Build/BatchFiles/RunUBT.sh -NoUBTBuildAccelerator UnrealEditor Linux Development


```

#### First make it Executable:
```bash
sudo chmod +x Scripts/build.sh
sudo chmod +x Scripts/clean_build.sh
sudo chmod +x Scripts/gen_server_target.sh
sudo chmod +x Scripts/copy_project_files.sh

```

####  Example Usage:
```bash
# Rebuild C++ code only (fast)
./Scripts/build.sh code

# Only blueprint changes
./Scripts/build.sh blueprints

# Full cook for content changes (no code changes)
./Scripts/build.sh content

# Build server binaries
./Scripts/build.sh server

# Full package (default)
./Scripts/build.sh full

# Clean build
./Scripts/clear_build.sh
```

| Mode         | Description                     | Cook | Build | Pak | Archive         |
| ------------ | ------------------------------- | ---- | ----- | --- | --------------- |
| `code`       | C++ only, no cook/pak/archive   | ❌    | ✅     | ❌   | ❌               |
| `blueprints` | Blueprint change only           | ✅    | ❌     | ✅   | ❌               |
| `content`    | Content-only changes            | ✅    | ❌     | ✅   | ❌               |
| `server`     | Server binaries only (new mode) | ❌    | ✅     | ❌   | ❌ (manual copy) |
| `full`       | Full cook + pak + archive       | ✅    | ✅     | ✅   | ✅               |


YourProjectNameServer is auto-generated when you enable Dedicated Server support.

Ensure you have `bUsesSteam=false` (if you're not configuring Steam) in DefaultEngine.ini under OnlineSubsystem.

### 5. Enable Server Target (if not done)

```bash
./Scripts/gen_server_target.sh
```

This creates a file like:
```bash
// YourProjectNameServer.Target.cs
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

## Clean Unreal Build Cache 

Run the following in your project folder, e.g.:
```bash
cd ~/UnrealProjects/YourProjectName
```

Then delete the following folders:
```bash
rm -rf Binaries/ Intermediate/ DerivedDataCache/ Saved/
```
#### Optional: Force Regenerate Project Files (if needed)
```bash
~/UnrealProjects/UnrealEngine/Engine/Build/BatchFiles/Linux/GenerateProjectFiles.sh \
  -project="$(pwd)/YourProjectName.uproject" -game
```

#### Rebuild the Project

Clean Build Cache (Optional if Build Breaks or Conflicts)

```bash
cd ~/UnrealProjects/YourProjectName

# Remove cached build files
rm -rf Binaries/ Intermediate/ DerivedDataCache/ Saved/

# Optional: Clean Unreal's build state
./UnrealProjects/UnrealEngine/Engine/Binaries/DotNET/UnrealBuildTool.exe -Clean

docker-compose down
docker-compose up --build
```

If you're just rebuilding code and not changing content:

```bash
./UnrealProjects/UnrealEngine/Engine/Binaries/DotNET/UnrealBuildTool.exe -Clean
rm -rf Saved Intermediate DerivedDataCache


docker-compose down
docker-compose up --build
```
<br>

## Dynamic Backend-API URLs, Views And Database Generation

#### Ecample `entities.json`

(DjangoBackend/config/[entities.json](config/entities.json))

  ```bash
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
    },
    ... add more fields if needed
}
  ```

<br>

  ### Troubleshooting


- #### Compile Error
  e.g.
  ```
  Compile Module.GeometryCollectionEngine.2.cpp
  In file included from /home/<username>/UnrealEngineGameServer/UnrealProjects/UnrealEngine/Engine/Intermediate/Build/Linux/x64/UnrealEditor/Development/GeometryCollectionEngine/Module.GeometryCollectionEngine.2.cpp:19:
  /home/jodermo/UnrealEngineGameServer/UnrealProjects/UnrealEngine/Engine/Source/Runtime/Experimental/GeometryCollectionEngine/Private/GeometryCollection/GeometryCollectionSceneProxy.cpp:43:10: fatal error: 'GeometryCollectionSceneProxy.ispc.generated.h' file not found
    43 | #include "GeometryCollectionSceneProxy.ispc.generated.h"
        |          ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  1 error generated.

  ```
  
  #### Solution: 
    Install ispc
    
    ```bash

# Go to Downloads
cd ~/Downloads

# Download ISPC 1.21.0 (LLVM 15.x – works with UE5.6)
wget https://github.com/ispc/ispc/releases/download/v1.21.0/ispc-v1.21.0-linux.tar.gz

# Extract
tar -xvzf ispc-v1.21.0-linux.tar.gz
cd ispc-v1.21.0-linux

# Install binary into /usr/local/bin (global path)
sudo cp bin/ispc /usr/local/bin/

# Verify version
ispc --version

# Alternative (project-local install)

mkdir -p ~/UnrealEngineGameServer/UnrealProjects/UnrealEngine/Engine/Binaries/ThirdParty/Linux/ISPC
cp bin/ispc ~/UnrealEngineGameServer/UnrealProjects/UnrealEngine/Engine/Binaries/ThirdParty/Linux/ISPC/

# Update PATH (optional but recommended)

echo 'export PATH=$HOME/UnrealEngineGameServer/UnrealProjects/UnrealEngine/Engine/Binaries/ThirdParty/Linux/ISPC:$PATH' >> ~/.bashrc
source ~/.bashrc



# rights for ispc

ls -l Engine/Binaries/ThirdParty/Linux/ISPC/ispc
chmod +x Engine/Binaries/ThirdParty/Linux/ISPC/ispc

    ```


You need to add the additional libraries to your build environment

```
sudo apt-get update && sudo apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libice6 \
    libxcomposite1 \
    libxrender1 \
    libfontconfig1 \
    libxss1 \
    libxtst6 \
    libxi6

```


# ispc problems:


```
# recommendation
./Engine/Build/BatchFiles/Linux/Build.sh UnrealEditor Linux Development -ForceSingleThread
find Engine/Intermediate -name "*.ispc.generated.h"


# other options

rm -rf Engine/Intermediate/Build/Linux/x86_64/UnrealEditor/Development/Chaos
./Engine/Build/BatchFiles/Linux/Build.sh UnrealEditor Linux Development -SingleFile
find Engine/Intermediate -name "*.ispc.generated.h"



rm -rf Engine/Intermediate
rm -rf Engine/Binaries/Linux




export UE_BUILD_DISABLE_ISPC=1
./Scripts/build.sh full


rm -rf Engine/Intermediate Engine/Binaries/Linux
./Scripts/build.sh full

```