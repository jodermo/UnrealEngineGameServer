# Unreal Engine Dedicated Server Runtime
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

ARG PROJECT_NAME=EvolutionGame
ARG BUILD_CONFIG=Shipping
ARG INSTALL_DEBUG_TOOLS=false
ARG USER_ID=1000
ARG GROUP_ID=1000

# Create non-root user with matching host UID/GID
RUN groupadd -g $GROUP_ID ue-server && \
    useradd -u $USER_ID -g $GROUP_ID -ms /bin/bash ue-server

# Install runtime dependencies
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

# Optionally install debug tools
RUN if [ "$INSTALL_DEBUG_TOOLS" = "true" ]; then \
      apt-get update && apt-get install -y --no-install-recommends \
      gdb strace file less vim && \
      rm -rf /var/lib/apt/lists/*; \
    fi

# Set working directory
WORKDIR /home/ue-server/${PROJECT_NAME}Server

# Validate build artifacts exist before copying
RUN echo "Validating build context..."
COPY UnrealProjects/${PROJECT_NAME}/Build/LinuxServer ./LinuxServer

# Copy launch script
COPY GameServer.sh ./GameServer.sh
RUN chmod +x ./GameServer.sh

# Set proper ownership
RUN chown -R ue-server:ue-server /home/ue-server/${PROJECT_NAME}Server

# Switch to non-root user
USER ue-server

# Create logs directory
RUN mkdir -p /home/ue-server/logs

# Expose ports
EXPOSE 7777/udp
EXPOSE 27015/udp

# Health check - test actual game port with longer startup time
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD nc -z -u 127.0.0.1 7777 || exit 1

ENTRYPOINT ["./GameServer.sh"]