"""
PersonalAI Dashcam Bridge Server

Ontvangt video streams van jailbroken dashcams en analyseert met AI.

Supported dashcams:
- Yi Dashcam (met custom firmware)
- 70mai (met UART/telnet access)
- Andere dashcams met RTSP output

Setup:
1. Jailbreak dashcam (zie hardware_configs/)
2. Start deze server op laptop/RPi in auto
3. Dashcam streamt → Server analyseert → Telegram alerts
"""

import sys
import logging
from pathlib import Path
from flask import Flask, request, jsonify
from typing import Dict, Optional
import cv2
import threading
import time

sys.path.append(str(Path(__file__).parent.parent))
import config
from modules.dashcam_ai import get_dashcam, EventType

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Connected dashcams
connected_dashcams: Dict[str, Dict] = {}

# PersonalAI dashcam instance
dashcam_ai = None


@app.route('/dashcam/register', methods=['GET'])
def register_dashcam():
    """
    Dashcam registration endpoint
    Called by jailbroken dashcam on boot

    Query params:
        ip: Dashcam IP address
        model: Optional dashcam model
    """
    ip = request.args.get('ip')
    model = request.args.get('model', 'Unknown')

    if not ip:
        return jsonify({'error': 'IP required'}), 400

    # Register dashcam
    connected_dashcams[ip] = {
        'model': model,
        'registered_at': time.time(),
        'last_seen': time.time(),
        'rtsp_url': f"rtsp://{ip}:554/stream"
    }

    logger.info(f"📹 Dashcam registered: {model} @ {ip}")

    # Start monitoring this dashcam
    start_dashcam_monitoring(ip)

    return jsonify({
        'status': 'registered',
        'ip': ip,
        'model': model,
        'message': 'PersonalAI will now monitor this dashcam'
    })


@app.route('/dashcam/analyze', methods=['POST'])
def analyze_frame():
    """
    Analyze frame from dashcam
    Called by dashcam bridge script with snapshot
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400

    file = request.files['file']
    ip = request.remote_addr

    # Save snapshot
    snapshot_path = config.CACHE_DIR / f"dashcam_{ip}_{int(time.time())}.jpg"
    file.save(snapshot_path)

    # Update last seen
    if ip in connected_dashcams:
        connected_dashcams[ip]['last_seen'] = time.time()

    # Analyze with AI (async to not block dashcam)
    threading.Thread(
        target=analyze_snapshot,
        args=(str(snapshot_path), ip),
        daemon=True
    ).start()

    return jsonify({'status': 'analyzing'})


def analyze_snapshot(image_path: str, dashcam_ip: str):
    """Analyze snapshot with RoboBrain"""
    global dashcam_ai

    if not dashcam_ai:
        logger.warning("Dashcam AI not initialized")
        return

    try:
        # Use dashcam_ai analyze method
        from core.brain import get_brain
        brain = get_brain()

        prompt = """
        Analyseer deze dashcam view voor veiligheid:

        1. Zie je gevaarlijke situaties?
        2. Verkeersborden?
        3. Afstand tot voertuig vooruit?
        4. Blijft auto in eigen rijstrook?
        5. Kentekens zichtbaar?

        Kort en direct.
        """

        result = brain.analyze(
            image=image_path,
            prompt=prompt,
            task="general",
            thinking=True
        )

        answer = result.get('answer', '').lower()

        # Trigger events based on analysis
        detect_events_from_analysis(answer, image_path, dashcam_ip)

        # Cleanup
        Path(image_path).unlink()

    except Exception as e:
        logger.error(f"Analysis error: {e}")


def detect_events_from_analysis(analysis: str, image_path: str, dashcam_ip: str):
    """Detect events from AI analysis"""

    # Import here to avoid circular import
    from modules.dashcam_ai import get_dashcam, EventType

    # Get or create dashcam instance for this IP
    # (In practice, you'd have one dashcam_ai per physical dashcam)

    # For now, log detected events
    if any(word in analysis for word in ['gevaar', 'collision', 'botsing']):
        logger.warning(f"⚠️ DANGER detected on dashcam {dashcam_ip}")
        # Trigger Telegram alert
        send_telegram_alert(f"⚠️ Gevaar gedetecteerd op dashcam {dashcam_ip}")

    if 'verkeersbord' in analysis or 'snelheidslimiet' in analysis:
        logger.info(f"🚦 Traffic sign detected on {dashcam_ip}")

    if 'kenteken' in analysis or 'nummerplaat' in analysis:
        logger.info(f"🚗 License plate detected on {dashcam_ip}")
        # Run ANPR
        run_anpr(image_path, dashcam_ip)


def run_anpr(image_path: str, dashcam_ip: str):
    """Run license plate recognition"""
    try:
        from modules.license_plate_ai import get_license_plate_ai

        lp_ai = get_license_plate_ai()
        plates = lp_ai.detect_plates(image_path)

        for plate in plates:
            logger.info(f"🚗 Plate detected: {plate.plate_number} (conf: {plate.confidence:.2f})")

            # Check whitelist/blacklist
            status = lp_ai.check_plate_status(plate.plate_number)
            if status == "blacklist":
                logger.warning(f"⚠️ BLACKLISTED PLATE: {plate.plate_number}")
                send_telegram_alert(f"⚠️ Blacklisted kenteken: {plate.plate_number}")

    except Exception as e:
        logger.error(f"ANPR error: {e}")


def send_telegram_alert(message: str):
    """Send Telegram alert (integration with bot)"""
    # In production: call Telegram bot API
    logger.info(f"📱 Telegram alert: {message}")
    # TODO: Implement actual Telegram sending


def start_dashcam_monitoring(dashcam_ip: str):
    """Start continuous monitoring of dashcam RTSP stream"""

    def monitor_rtsp_stream():
        rtsp_url = connected_dashcams[dashcam_ip]['rtsp_url']
        logger.info(f"📹 Starting RTSP monitoring: {rtsp_url}")

        # Open RTSP stream with OpenCV
        cap = cv2.VideoCapture(rtsp_url)

        if not cap.isOpened():
            logger.error(f"Failed to open RTSP stream: {rtsp_url}")
            return

        frame_count = 0
        analysis_interval = 60  # Analyze every 60 frames (~2 sec at 30fps)

        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"Stream ended or error: {rtsp_url}")
                time.sleep(5)
                # Reconnect
                cap = cv2.VideoCapture(rtsp_url)
                continue

            frame_count += 1

            # Analyze every N frames
            if frame_count % analysis_interval == 0:
                # Save frame
                snapshot_path = config.CACHE_DIR / f"rtsp_{dashcam_ip}_{int(time.time())}.jpg"
                cv2.imwrite(str(snapshot_path), frame)

                # Analyze
                threading.Thread(
                    target=analyze_snapshot,
                    args=(str(snapshot_path), dashcam_ip),
                    daemon=True
                ).start()

            # Check if dashcam still connected
            if time.time() - connected_dashcams[dashcam_ip]['last_seen'] > 60:
                logger.warning(f"Dashcam {dashcam_ip} disconnected")
                break

        cap.release()

    # Start monitoring thread
    threading.Thread(target=monitor_rtsp_stream, daemon=True).start()


@app.route('/dashcam/status', methods=['GET'])
def get_status():
    """Get status of all connected dashcams"""
    return jsonify({
        'connected_dashcams': len(connected_dashcams),
        'dashcams': [
            {
                'ip': ip,
                'model': info['model'],
                'last_seen': time.time() - info['last_seen'],
                'rtsp_url': info['rtsp_url']
            }
            for ip, info in connected_dashcams.items()
        ]
    })


@app.route('/dashcam/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'status': 'PersonalAI Dashcam Bridge Server',
        'version': '1.0',
        'ready': True
    })


def main():
    """Start bridge server"""
    global dashcam_ai

    print("🚗 PersonalAI Dashcam Bridge Server")
    print("=" * 50)
    print()
    print("📡 Listening for jailbroken dashcams...")
    print("📍 Server: http://0.0.0.0:5000")
    print()
    print("Setup instructions:")
    print("1. Jailbreak your dashcam (see hardware_configs/)")
    print("2. Install personalai_bridge.sh on dashcam")
    print("3. Set PERSONALAI_SERVER to this computer's IP")
    print("4. Reboot dashcam")
    print()
    print("Waiting for dashcam connections...")
    print()

    # Initialize dashcam AI
    try:
        dashcam_ai = get_dashcam()
        print("✅ Dashcam AI initialized")
    except Exception as e:
        print(f"⚠️ Dashcam AI init warning: {e}")

    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)


if __name__ == "__main__":
    main()
