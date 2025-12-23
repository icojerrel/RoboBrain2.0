"""
PersonalAI Live Camera Monitor
Real-time webcam en IP camera monitoring met AI vision
"""

import sys
import cv2
import time
import threading
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class CameraType(Enum):
    """Camera types"""
    WEBCAM = "webcam"
    IP_CAMERA = "ip_camera"
    RTSP = "rtsp"
    FILE = "file"


@dataclass
class CameraConfig:
    """Camera configuratie"""
    name: str
    camera_type: CameraType
    source: str  # Device ID, URL, of file path
    fps: int = 30
    resolution: tuple = (1920, 1080)
    enabled: bool = True


class CameraStream:
    """
    Live camera stream handler
    Supports webcams, IP cameras, RTSP streams
    """

    def __init__(self, config: CameraConfig):
        self.config = config
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.last_frame = None
        self.frame_count = 0
        self.start_time = None

        # Frame buffer voor processing
        self.frame_buffer = []
        self.max_buffer_size = 30  # 1 second at 30fps

        # Callbacks
        self.frame_callbacks: List[Callable] = []

        logger.info(f"📹 Camera stream configured: {config.name}")

    def start(self) -> bool:
        """Start camera stream"""
        try:
            # Open camera
            if self.config.camera_type == CameraType.WEBCAM:
                # Webcam (integer device ID)
                self.cap = cv2.VideoCapture(int(self.config.source))
            elif self.config.camera_type in [CameraType.IP_CAMERA, CameraType.RTSP]:
                # IP camera or RTSP stream
                self.cap = cv2.VideoCapture(self.config.source)
            elif self.config.camera_type == CameraType.FILE:
                # Video file
                self.cap = cv2.VideoCapture(self.config.source)

            if not self.cap.isOpened():
                logger.error(f"❌ Kan camera niet openen: {self.config.source}")
                return False

            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)

            self.is_running = True
            self.start_time = time.time()

            logger.info(f"✅ Camera stream started: {self.config.name}")
            return True

        except Exception as e:
            logger.error(f"❌ Error starting camera: {e}")
            return False

    def stop(self):
        """Stop camera stream"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        logger.info(f"🛑 Camera stream stopped: {self.config.name}")

    def read_frame(self) -> Optional[np.ndarray]:
        """
        Lees een frame van de camera

        Returns:
            Numpy array (BGR) of None
        """
        if not self.is_running or not self.cap:
            return None

        ret, frame = self.cap.read()
        if ret:
            self.last_frame = frame
            self.frame_count += 1

            # Add to buffer
            self.frame_buffer.append(frame)
            if len(self.frame_buffer) > self.max_buffer_size:
                self.frame_buffer.pop(0)

            # Call callbacks
            for callback in self.frame_callbacks:
                try:
                    callback(frame)
                except Exception as e:
                    logger.error(f"Callback error: {e}")

            return frame
        else:
            logger.warning(f"⚠️ Failed to read frame from {self.config.name}")
            return None

    def get_snapshot(self, output_path: str = None) -> str:
        """
        Neem snapshot

        Args:
            output_path: Pad om snapshot op te slaan

        Returns:
            Path naar snapshot
        """
        if self.last_frame is None:
            logger.error("Geen frame beschikbaar voor snapshot")
            return None

        if output_path is None:
            timestamp = int(time.time())
            output_path = str(config.CACHE_DIR / f"snapshot_{self.config.name}_{timestamp}.jpg")

        cv2.imwrite(output_path, self.last_frame)
        logger.info(f"📸 Snapshot saved: {output_path}")
        return output_path

    def add_frame_callback(self, callback: Callable):
        """Voeg callback toe voor elke frame"""
        self.frame_callbacks.append(callback)

    def get_stats(self) -> Dict:
        """Krijg stream statistieken"""
        if not self.start_time:
            return {}

        runtime = time.time() - self.start_time
        actual_fps = self.frame_count / runtime if runtime > 0 else 0

        return {
            'name': self.config.name,
            'is_running': self.is_running,
            'frame_count': self.frame_count,
            'runtime': round(runtime, 1),
            'fps': round(actual_fps, 1),
            'resolution': self.config.resolution,
            'buffer_size': len(self.frame_buffer)
        }


class CameraManager:
    """
    Beheer meerdere camera streams
    """

    def __init__(self):
        self.cameras: Dict[str, CameraStream] = {}
        self.monitoring_thread: Optional[threading.Thread] = None
        self.is_monitoring = False

        logger.info("📹 Camera Manager geïnitialiseerd")

    def add_camera(self, config: CameraConfig) -> bool:
        """Voeg camera toe"""
        if config.name in self.cameras:
            logger.warning(f"Camera '{config.name}' bestaat al")
            return False

        stream = CameraStream(config)
        self.cameras[config.name] = stream

        logger.info(f"➕ Camera toegevoegd: {config.name}")
        return True

    def remove_camera(self, name: str) -> bool:
        """Verwijder camera"""
        if name not in self.cameras:
            return False

        self.cameras[name].stop()
        del self.cameras[name]

        logger.info(f"➖ Camera verwijderd: {name}")
        return True

    def start_camera(self, name: str) -> bool:
        """Start specifieke camera"""
        if name not in self.cameras:
            logger.error(f"Camera '{name}' niet gevonden")
            return False

        return self.cameras[name].start()

    def stop_camera(self, name: str) -> bool:
        """Stop specifieke camera"""
        if name not in self.cameras:
            return False

        self.cameras[name].stop()
        return True

    def start_all(self):
        """Start alle camera's"""
        for name, camera in self.cameras.items():
            if camera.config.enabled:
                camera.start()

        logger.info(f"🎬 {len(self.cameras)} camera's gestart")

    def stop_all(self):
        """Stop alle camera's"""
        for camera in self.cameras.values():
            camera.stop()

        logger.info("🛑 Alle camera's gestopt")

    def get_snapshot(self, name: str, output_path: str = None) -> str:
        """Neem snapshot van camera"""
        if name not in self.cameras:
            return None

        return self.cameras[name].get_snapshot(output_path)

    def get_camera(self, name: str) -> Optional[CameraStream]:
        """Krijg camera stream"""
        return self.cameras.get(name)

    def list_cameras(self) -> List[Dict]:
        """Lijst alle camera's"""
        return [
            {
                'name': name,
                'type': cam.config.camera_type.value,
                'source': cam.config.source,
                'enabled': cam.config.enabled,
                'running': cam.is_running
            }
            for name, cam in self.cameras.items()
        ]

    def get_all_stats(self) -> Dict:
        """Krijg statistieken van alle camera's"""
        return {
            name: cam.get_stats()
            for name, cam in self.cameras.items()
        }

    def start_monitoring(self, interval: float = 1.0):
        """
        Start continuous monitoring van alle cameras

        Args:
            interval: Tijd tussen checks in seconden
        """
        if self.is_monitoring:
            logger.warning("Monitoring is al actief")
            return

        self.is_monitoring = True

        def monitor_loop():
            logger.info("🔄 Monitoring gestart")
            while self.is_monitoring:
                for name, camera in self.cameras.items():
                    if camera.is_running:
                        camera.read_frame()
                time.sleep(interval)

        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

        logger.info("⏸️ Monitoring gestopt")


# Singleton instance
_camera_manager: Optional[CameraManager] = None


def get_camera_manager() -> CameraManager:
    """Krijg of maak camera manager (singleton)"""
    global _camera_manager
    if _camera_manager is None:
        _camera_manager = CameraManager()
    return _camera_manager


def detect_webcams() -> List[int]:
    """
    Detecteer beschikbare webcams

    Returns:
        List van webcam device IDs
    """
    available = []
    for i in range(10):  # Check first 10 devices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()

    logger.info(f"🔍 {len(available)} webcam(s) gevonden: {available}")
    return available


# Test code
if __name__ == "__main__":
    print("📹 Camera Monitor Test\n")

    # Detecteer webcams
    webcams = detect_webcams()

    if not webcams:
        print("❌ Geen webcams gevonden!")
        print("💡 Test met een video file of IP camera URL")
    else:
        # Test met eerste webcam
        manager = get_camera_manager()

        config = CameraConfig(
            name="test_webcam",
            camera_type=CameraType.WEBCAM,
            source="0",
            fps=30
        )

        manager.add_camera(config)
        manager.start_camera("test_webcam")

        # Neem snapshot
        time.sleep(2)  # Wait for camera to warm up
        snapshot = manager.get_snapshot("test_webcam")
        print(f"📸 Snapshot: {snapshot}")

        # Stats
        stats = manager.get_all_stats()
        print(f"\n📊 Stats: {stats}")

        # Stop
        manager.stop_camera("test_webcam")

    print("\n✅ Camera monitor test compleet!")
