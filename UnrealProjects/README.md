# UnrealProjects – Source Projects for Unreal Engine

#### Ecample Structure:

```bash
UnrealProjects/
├── UnrealEngine/         # Cloned Unreal Engine source (Linux build)
│   ├── Engine/
│   ├── Setup.sh
│   └── ...
├── YourProjectName/      # Your actual game project
│   ├── Binaries/
│   ├── Config/
│   ├── Content/
│   ├── Source/
│   └── YourProjectName.uproject
```


## Setup Instructions


#### 1. Clone Unreal Engine (access required)

```bash
git clone --depth=1 -b 5.6 https://github.com/EpicGames/UnrealEngine.git
```


####  2. Build the Engine for Linux

```bash
cd UnrealEngine
./Setup.sh
./GenerateProjectFiles.sh
make

```
#### 3. Copy Or Clone Your Project to UnrealProjects

- Option A: Copy from Windows

    ```bash

    mkdir -p ~/UnrealProjects/YourProjectName
    cp -r /mnt/c/Path/To/Your/WindowsProject/* ~/UnrealProjects/YourProjectName/

    ```
- Option B: Clone from Git

    ```bash
    cd ~/UnrealProjects
    git clone https://github.com/yourusername/YourProjectName.git

    ```

#### 4. Build Your Game Server

Use Unreal’s RunUAT.sh script to build, cook, and package your game for Linux dedicated server deployment:

```bash
./UnrealProjects/UnrealEngine/Engine/Build/BatchFiles/RunUAT.sh BuildCookRun \
 -project="$(pwd)/UnrealProjects/YourProjectName/YourProjectName.uproject" \
 -noP4 \
 -platform=Linux \
 -targetplatform=Linux \
 -clientconfig=Shipping \
 -serverconfig=Shipping \
 -cook -allmaps \
 -build \
 -stage \
 -pak \
 -archive \
 -archivedirectory="$(pwd)/Packaged/YourProjectName" \
 -server \
 -serverplatform=Linux

```

