#!/bin/bash
# VTT-Node | MapTool Entrypoint - Post-review (array args fix)
set -e
echo "[VTT-Node] Starting MapTool ${MAPTOOL_VERSION:-unknown}..."
Xvfb :99 -screen 0 1280x800x24 -nolisten tcp & XVFB_PID=$! && sleep 2
x11vnc -display :99 -forever -shared -nopw -listen 0.0.0.0 -port 5900 -quiet & VNC_PID=$!
websockify --web /usr/share/novnc/ 6080 localhost:5900 & NOVNC_PID=$!

# Array args - safe for spaces in server names (fixed from unquoted string)
MT_ARGS=(-port "${MT_PORT:-51234}" -server)
[ -n "$MT_SERVER_NAME" ] && MT_ARGS+=(-name "$MT_SERVER_NAME")
[ -n "$MT_SERVER_PASSWORD" ] && MT_ARGS+=(-password "$MT_SERVER_PASSWORD")
[ -n "$MT_GM_PASSWORD" ] && MT_ARGS+=(-gmpassword "$MT_GM_PASSWORD")
[ -f "/data/maptool/campaigns/default.cmpgn" ] && MT_ARGS+=(/data/maptool/campaigns/default.cmpgn)

JAVA_OPTS="${JAVA_OPTS:--Xmx2048m}"
if [ -f /usr/local/bin/maptool.AppImage ]; then
    DISPLAY=:99 /usr/local/bin/maptool.AppImage "${MT_ARGS[@]}" &
else
    DISPLAY=:99 java $JAVA_OPTS -jar /opt/maptool/MapTool.jar "${MT_ARGS[@]}" &
fi
MT_PID=$!

for i in $(seq 1 30); do
    nc -z localhost ${MT_PORT:-51234} 2>/dev/null && echo "[VTT-Node] Ready" && break
    sleep 2
done

cleanup() { kill $MT_PID $NOVNC_PID $VNC_PID $XVFB_PID 2>/dev/null; wait; }
trap cleanup SIGTERM SIGINT
wait $MT_PID