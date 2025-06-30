# Build Sripts

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