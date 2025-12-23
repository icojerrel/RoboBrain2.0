#!/bin/sh
# PersonalAI Bridge voor Yi Dashcam
# Draait OP de dashcam en streamt naar PersonalAI server

PERSONALAI_SERVER="192.168.43.1"  # Computer/RPi met PersonalAI
RTSP_PORT="554"

echo "PersonalAI Bridge Starting..."

# Wait for network
sleep 10

# Check if PersonalAI server reachable
ping -c 1 $PERSONALAI_SERVER
if [ $? -ne 0 ]; then
    echo "ERROR: PersonalAI server not reachable"
    exit 1
fi

# Start RTSP server op dashcam
killall rtspsvr 2>/dev/null
/tmp/sd/rtspsvr -p $RTSP_PORT &

echo "RTSP stream active on port $RTSP_PORT"

# Notify PersonalAI server via HTTP
wget -O - "http://$PERSONALAI_SERVER:5000/dashcam/register?ip=$(ifconfig wlan0 | grep 'inet addr' | cut -d: -f2 | awk '{print $1}')" 2>/dev/null

# Send periodic snapshots to PersonalAI
while true; do
    # Capture frame van video stream
    ffmpeg -i rtsp://127.0.0.1:554/stream -vframes 1 /tmp/snapshot.jpg -y 2>/dev/null

    # Upload naar PersonalAI server voor analyse
    curl -F "file=@/tmp/snapshot.jpg" http://$PERSONALAI_SERVER:5000/dashcam/analyze 2>/dev/null

    # Elke 2 seconden (PersonalAI analysis interval)
    sleep 2
done
