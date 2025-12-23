#!/bin/bash
# Yi Dashcam Jailbreak & RTSP Streamer
# Plaats dit bestand als autoexec.ash op SD card root

echo "=== Yi Dashcam Custom Boot ==="

# Enable telnet
telnetd &

# Start RTSP server voor video streaming
sleep 5
/tmp/sd/rtspsvr &

# Custom settings
echo "Enabling WiFi..."
/usr/local/share/script/wifi.sh

# Set custom video settings
echo "Setting 1080p 60fps..."
/usr/local/share/script/videores.sh 1080p_60

# Enable GPS logging (if GPS module present)
echo "Enabling GPS..."
/tmp/sd/gps_enable.sh &

# Start custom script voor PersonalAI integratie
echo "Starting PersonalAI bridge..."
/tmp/sd/personalai_bridge.sh &

echo "=== Yi Dashcam Jailbreak Complete ==="
echo "RTSP stream: rtsp://192.168.1.254:554/stream"
echo "Telnet: telnet 192.168.1.254"

# Keep running
while true; do
    sleep 3600
done
