# Use minimal Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Build arguments for project name and archive directory
ARG PROJECT_NAME=UnrealEngineGame
ARG PROJECT_DIR=UnrealProjects/YourProjectName
ARG ARCHIVE_DIR=Packaged/YourProjectName

# Set environment variables for use during runtime
ENV PROJECT_NAME=${PROJECT_NAME}
ENV PROJECT_DIR=${PROJECT_DIR}
ENV ARCHIVE_DIR=${ARCHIVE_DIR}

# Metadata
LABEL maintainer="Moritz Petzka - info@petzka.com"
LABEL project="${PROJECT_NAME} - Dedicated Server"

# Create a non-root user for better security
RUN useradd -ms /bin/bash ue-server

# Install only necessary runtime libraries to keep image minimal
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 libstdc++6 libx11-6 libxcb1 libxrandr2 libxinerama1 libxcursor1 libxi6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory for the application
WORKDIR /home/ue-server

# Copy the server launch script into the container
COPY ./GameServer.sh ./

# Now use the values directly
COPY ${PROJECT_DIR}/${PROJECT_NAME}.uproject ./UnrealProjects/${PROJECT_NAME}/
COPY ${PROJECT_DIR}/Content ./UnrealProjects/${PROJECT_NAME}/Content/
COPY ${PROJECT_DIR}/Config ./UnrealProjects/${PROJECT_NAME}/Config/
COPY ${ARCHIVE_DIR}/ ./UnrealProjects/${PROJECT_NAME}/LinuxServer/

# Set file permissions and ownership
RUN chown -R ue-server:ue-server /home/ue-server && \
    chmod +x ./GameServer.sh

# Use the non-root user from here on
USER ue-server

# Expose Unreal's default game port (7777 UDP) and optional control port (15000 TCP)
EXPOSE 7777/udp 15000/tcp

# Define health check to ensure the game server is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD pgrep -f "${PROJECT_NAME}Server" || exit 1

# Start the server using the launch script
ENTRYPOINT ["/home/ue-server/GameServer.sh"]
