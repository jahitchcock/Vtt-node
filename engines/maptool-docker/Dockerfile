# =============================================================================
# VTT-Node | engines/maptool-docker/Dockerfile
# Headless MapTool via Xvfb + noVNC
# =============================================================================

FROM ubuntu:24.04

ARG MAPTOOL_VERSION=1.14.0

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:99 \
    MT_PORT=51234 \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless xvfb x11vnc novnc websockify wget curl \
    netcat-openbsd libxrender1 libxtst6 libxi6 fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 -s /bin/bash maptool
WORKDIR /home/maptool

RUN wget -q "https://github.com/RPTools/maptool/releases/download/${MAPTOOL_VERSION}/MapTool-${MAPTOOL_VERSION}-x64.deb" \
    -O /tmp/maptool.deb && dpkg -i /tmp/maptool.deb && rm /tmp/maptool.deb \
    || wget -q "https://github.com/RPTools/maptool/releases/download/${MAPTOOL_VERSION}/maptool-${MAPTOOL_VERSION}-linux-x64.AppImage" \
    -O /usr/local/bin/maptool.AppImage && chmod +x /usr/local/bin/maptool.AppImage

RUN mkdir -p /data/maptool/campaigns /data/maptool/assets \
    && chown -R maptool:maptool /data

RUN ln -s /usr/share/novnc/vnc.html /usr/share/novnc/index.html 2>/dev/null || true

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER maptool
EXPOSE 51234 5900 6080
ENTRYPOINT ["/entrypoint.sh"]
