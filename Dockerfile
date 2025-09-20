# Unreal Engine Dedicated Server Runtime
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

ARG PROJECT_NAME=EvolutionGame
ARG BUILD_CONFIG=Shipping
ARG INSTALL_DEBUG_TOOLS=false   # set to true for debug builds

# Create non-root user
RUN useradd -ms /bin/bash ue-server

# Install runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libicu70 \
    libssl3 \
    libncurses5 \
    libnss3 \
    libx11-6 \
    libxcb1 \
    libxcomposite1 \
    libxrandr2 \
    libxi6 \
    libasound2 \
    libglib2.0-0 \
    libstdc++6 \
    zlib1g \
    libcurl4 \
    libgtk-3-0 \
    libxinerama1 \
    libxrender1 \
    libgl1 \
    libvulkan1 \
    mesa-vulkan-drivers \
    libxss1 \
    libxft2 \
    libxcb-xinput0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libtinfo6 \
    xdg-user-dirs \
    ca-certificates \
    curl \
    net-tools \
    iproute2 \
    procps \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*


# Optionally install debug tools (use --build-arg INSTALL_DEBUG_TOOLS=true)
RUN if [ "$INSTALL_DEBUG_TOOLS" = "true" ]; then \
      apt-get update && apt-get install -y --no-install-recommends \
      gdb strace file less vim && \
      rm -rf /var/lib/apt/lists/*; \
    fi

# Working directory points to packaged build root
WORKDIR /home/ue-server/${PROJECT_NAME}Server

# Copy entire packaged dedicated server (LinuxServer folder)
COPY UnrealProjects/${PROJECT_NAME}/Build/LinuxServer/ ./

# Copy launch script
COPY GameServer.sh GameServer.sh
RUN chmod +x GameServer.sh

# Permissions
RUN chown -R ue-server:ue-server /home/ue-server/${PROJECT_NAME}Server

USER ue-server

EXPOSE 7777/udp
EXPOSE 27015/udp

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD nc -z -u 127.0.0.1 27015 || exit 1

ENTRYPOINT ["./GameServer.sh"]
