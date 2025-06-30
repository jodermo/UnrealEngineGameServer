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

Use scripts to build, cook, and package your game for Linux dedicated server deployment:

```bash
# Rebuild C++ code only (fast)
./Scripts/build.sh code

# Only blueprint changes
./Scripts/build.sh blueprints

# Full cook for content changes (no code changes)
./Scripts/build.sh content

# Full package (default)
./Scripts/build.sh full
```

