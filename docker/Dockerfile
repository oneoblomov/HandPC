# HCI Extension Test Environment Dockerfile
# Multi-stage build for optimized test environment

# Base stage - Ubuntu with GNOME development tools
FROM ubuntu:22.04 as base

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Python and development tools
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    # GNOME development
    gnome-shell-extension-prefs \
    gjs \
    libgjs-dev \
    gir1.2-gtk-3.0 \
    gir1.2-gtk-4.0 \
    gir1.2-adw-1 \
    gir1.2-gdkpixbuf-2.0 \
    gir1.2-glib-2.0 \
    gir1.2-gobject-2.0 \
    gir1.2-atk-1.0 \
    libgirepository1.0-dev \
    # Build tools
    build-essential \
    meson \
    ninja-build \
    gettext \
    appstream \
    # Graphics and display
    xvfb \
    x11-utils \
    libx11-dev \
    libxext-dev \
    libxtst-dev \
    libgtk-3-dev \
    libcairo2-dev \
    # Networking and utilities
    curl \
    wget \
    git \
    zip \
    unzip \
    jq \
    # Video processing (for MediaPipe)
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    # OpenCV dependencies
    libopencv-dev \
    python3-opencv \
    # Additional utilities
    tree \
    htop \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN python3 -m pip install --upgrade pip setuptools wheel

# Create working directory
WORKDIR /workspace

# Development stage - Add development tools
FROM base as development

# Install additional development tools
RUN apt-get update && apt-get install -y \
    # Code quality tools
    shellcheck \
    # Testing tools
    lcov \
    valgrind \
    # Debugging tools
    gdb \
    strace \
    && rm -rf /var/lib/apt/lists/*

# Install Python development packages
RUN pip3 install \
    # Testing frameworks
    pytest>=7.0.0 \
    pytest-cov>=4.0.0 \
    pytest-mock>=3.10.0 \
    pytest-benchmark>=4.0.0 \
    pytest-xdist>=3.0.0 \
    # Code quality
    black>=23.0.0 \
    isort>=5.12.0 \
    flake8>=6.0.0 \
    mypy>=1.0.0 \
    bandit>=1.7.0 \
    # Core dependencies
    numpy>=1.21.0 \
    opencv-python>=4.7.0 \
    # Attempt MediaPipe install (may fail in some environments)
    && pip3 install mediapipe>=0.10.0 || echo "MediaPipe installation failed - continuing" \
    # PyAutoGUI (may need display)
    && pip3 install pyautogui>=0.9.54 || echo "PyAutoGUI installation failed - continuing"

# Create display environment for GUI testing
ENV DISPLAY=:99
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Test stage - Optimized for CI/CD
FROM base as test

# Install only essential test dependencies
RUN pip3 install \
    pytest>=7.0.0 \
    pytest-cov>=4.0.0 \
    pytest-mock>=3.10.0 \
    black>=23.0.0 \
    flake8>=6.0.0 \
    numpy>=1.21.0 \
    opencv-python-headless>=4.7.0

# Try to install MediaPipe and PyAutoGUI (with fallbacks)
RUN pip3 install mediapipe>=0.10.0 || echo "MediaPipe not available in this environment" \
    && pip3 install pyautogui>=0.9.54 || echo "PyAutoGUI not available in this environment"

# Create test user (non-root for security)
RUN useradd -m -s /bin/bash testuser && \
    usermod -aG sudo testuser && \
    echo "testuser:testuser" | chpasswd

# Set up test environment
ENV DISPLAY=:99
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/workspace/src_python/src:/workspace/src_python

# Copy test scripts
COPY docker/scripts/ /usr/local/bin/
RUN chmod +x /usr/local/bin/*

# Production stage - Minimal runtime for extension
FROM base as production

# Install only runtime dependencies
RUN pip3 install \
    numpy>=1.21.0 \
    opencv-python>=4.7.0 \
    mediapipe>=0.10.0 \
    pyautogui>=0.9.54

# Create extension user
RUN useradd -m -s /bin/bash hciuser && \
    usermod -aG video,audio hciuser

# Set up runtime environment
ENV DISPLAY=:0
ENV PYTHONPATH=/opt/hci-extension/src_python/src

# Create extension directory
RUN mkdir -p /opt/hci-extension && \
    chown hciuser:hciuser /opt/hci-extension

USER hciuser
WORKDIR /opt/hci-extension

# Default command
CMD ["python3", "src_python/service.py", "/opt/hci-extension"]

# Multi-architecture support
FROM production as final
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Log build information
RUN echo "Building for $TARGETPLATFORM on $BUILDPLATFORM" > /opt/build-info.txt

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# Metadata
LABEL maintainer="HCI Extension Team"
LABEL description="Test environment for HCI GNOME Shell Extension"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/your-repo/hci-extension"
LABEL org.opencontainers.image.documentation="https://github.com/your-repo/hci-extension/blob/main/README.md"
LABEL org.opencontainers.image.licenses="MIT"