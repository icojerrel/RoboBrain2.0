"""
PersonalAI EZVIZ Camera Integration
Specifieke ondersteuning voor EZVIZ Husky Air en andere EZVIZ cameras
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass

sys.path.append(str(Path(__file__).parent.parent))
import config
from modules.camera_monitor import CameraConfig, CameraType, get_camera_manager

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


@dataclass
class EZVIZConfig:
    """EZVIZ camera configuratie"""
    name: str
    ip_address: str
    username: str = "admin"
    password: str = ""
    rtsp_port: int = 554
    http_port: int = 80
    channel: int = 1  # Main stream = 1, Sub stream = 2
    model: str = "Husky Air"


class EZVIZCamera:
    """
    EZVIZ Camera helper
    Specifiek voor EZVIZ Husky Air en compatible models
    """

    def __init__(self, config: EZVIZConfig):
        self.config = config
        self.camera_manager = get_camera_manager()

        logger.info(f"📹 EZVIZ {config.model} configured: {config.name}")

    def get_rtsp_url(self, stream: str = "main") -> str:
        """
        Bouw RTSP URL voor EZVIZ camera

        Args:
            stream: "main" voor hoofdstream (hoge kwaliteit)
                   "sub" voor substream (lage kwaliteit, minder bandwidth)

        Returns:
            RTSP URL
        """
        # EZVIZ RTSP format:
        # rtsp://username:password@ip:port/h264/ch{channel}/{stream_type}/av_stream

        channel = "01" if self.config.channel == 1 else f"{self.config.channel:02d}"
        stream_type = "main" if stream == "main" else "sub"

        if self.config.password:
            auth = f"{self.config.username}:{self.config.password}@"
        else:
            auth = ""

        url = (
            f"rtsp://{auth}{self.config.ip_address}:{self.config.rtsp_port}/"
            f"h264/ch{channel}/{stream_type}/av_stream"
        )

        return url

    def add_to_manager(self, stream: str = "main", fps: int = 15) -> bool:
        """
        Voeg camera toe aan camera manager

        Args:
            stream: "main" of "sub"
            fps: Frames per second

        Returns:
            Success boolean
        """
        rtsp_url = self.get_rtsp_url(stream)

        cam_config = CameraConfig(
            name=f"{self.config.name}_{stream}",
            camera_type=CameraType.RTSP,
            source=rtsp_url,
            fps=fps,
            resolution=(1920, 1080) if stream == "main" else (640, 480)
        )

        success = self.camera_manager.add_camera(cam_config)

        if success:
            logger.info(f"✅ EZVIZ camera toegevoegd: {cam_config.name}")
        else:
            logger.error(f"❌ Kon EZVIZ camera niet toevoegen")

        return success

    def start_stream(self, stream: str = "main") -> bool:
        """Start camera stream"""
        cam_name = f"{self.config.name}_{stream}"
        return self.camera_manager.start_camera(cam_name)

    def stop_stream(self, stream: str = "main") -> bool:
        """Stop camera stream"""
        cam_name = f"{self.config.name}_{stream}"
        return self.camera_manager.stop_camera(cam_name)

    def get_snapshot(self, stream: str = "main") -> str:
        """Neem snapshot"""
        cam_name = f"{self.config.name}_{stream}"
        return self.camera_manager.get_snapshot(cam_name)

    def get_camera_info(self) -> Dict:
        """Krijg camera informatie"""
        return {
            'name': self.config.name,
            'model': self.config.model,
            'ip': self.config.ip_address,
            'rtsp_port': self.config.rtsp_port,
            'main_stream': self.get_rtsp_url("main"),
            'sub_stream': self.get_rtsp_url("sub")
        }

    @staticmethod
    def quick_setup_husky_air(name: str, ip: str, password: str) -> 'EZVIZCamera':
        """
        Quick setup voor EZVIZ Husky Air

        Args:
            name: Camera naam
            ip: IP adres (bijv. "192.168.1.100")
            password: Camera wachtwoord

        Returns:
            Configured EZVIZCamera instance
        """
        config = EZVIZConfig(
            name=name,
            ip_address=ip,
            username="admin",
            password=password,
            model="Husky Air"
        )

        camera = EZVIZCamera(config)
        logger.info("✅ EZVIZ Husky Air quick setup compleet!")

        return camera


class EZVIZManager:
    """
    Beheer meerdere EZVIZ camera's
    """

    def __init__(self):
        self.cameras: Dict[str, EZVIZCamera] = {}
        self.camera_manager = get_camera_manager()

        logger.info("📹 EZVIZ Manager geïnitialiseerd")

    def add_husky_air(self, name: str, ip: str, password: str) -> EZVIZCamera:
        """
        Voeg EZVIZ Husky Air toe

        Args:
            name: Camera naam
            ip: IP adres
            password: Wachtwoord

        Returns:
            EZVIZCamera instance
        """
        camera = EZVIZCamera.quick_setup_husky_air(name, ip, password)
        self.cameras[name] = camera

        # Add main stream (hoge kwaliteit)
        camera.add_to_manager(stream="main", fps=15)

        # Add sub stream (lage kwaliteit voor monitoring)
        camera.add_to_manager(stream="sub", fps=10)

        logger.info(f"➕ EZVIZ Husky Air toegevoegd: {name}")
        return camera

    def add_custom_ezviz(self, config: EZVIZConfig) -> EZVIZCamera:
        """Voeg custom EZVIZ camera toe"""
        camera = EZVIZCamera(config)
        self.cameras[config.name] = camera

        camera.add_to_manager(stream="main")
        camera.add_to_manager(stream="sub")

        logger.info(f"➕ EZVIZ camera toegevoegd: {config.name}")
        return camera

    def get_camera(self, name: str) -> Optional[EZVIZCamera]:
        """Krijg camera by name"""
        return self.cameras.get(name)

    def list_cameras(self) -> List[Dict]:
        """Lijst alle EZVIZ cameras"""
        return [cam.get_camera_info() for cam in self.cameras.values()]

    def start_all(self, stream: str = "sub"):
        """
        Start alle EZVIZ cameras

        Args:
            stream: "main" of "sub" (default: sub voor lagere bandwidth)
        """
        for name, camera in self.cameras.items():
            camera.start_stream(stream)

        logger.info(f"🎬 {len(self.cameras)} EZVIZ camera's gestart ({stream} stream)")

    def stop_all(self):
        """Stop alle cameras"""
        for camera in self.cameras.values():
            camera.stop_stream("main")
            camera.stop_stream("sub")

        logger.info("🛑 Alle EZVIZ camera's gestopt")


# Singleton
_ezviz_manager: Optional[EZVIZManager] = None


def get_ezviz_manager() -> EZVIZManager:
    """Krijg EZVIZ manager (singleton)"""
    global _ezviz_manager
    if _ezviz_manager is None:
        _ezviz_manager = EZVIZManager()
    return _ezviz_manager


# Helper functions
def setup_husky_air(name: str = "HuskyAir", ip: str = None, password: str = None) -> EZVIZCamera:
    """
    Quick setup function voor EZVIZ Husky Air

    Args:
        name: Camera naam
        ip: IP adres (None = vraag gebruiker)
        password: Wachtwoord (None = geen wachtwoord)

    Returns:
        Configured camera
    """
    if ip is None:
        print("❓ Wat is het IP adres van je EZVIZ Husky Air?")
        print("   (Bijv: 192.168.1.100)")
        print("   💡 Check je router of EZVIZ app voor het IP adres")
        ip = input("   IP: ").strip()

    if password is None:
        print("\n❓ Wat is het camera wachtwoord?")
        print("   (Laat leeg als geen wachtwoord)")
        password = input("   Wachtwoord: ").strip()

    manager = get_ezviz_manager()
    camera = manager.add_husky_air(name, ip, password)

    print(f"\n✅ EZVIZ Husky Air setup compleet!")
    print(f"📹 Camera naam: {name}")
    print(f"🌐 IP adres: {ip}")
    print(f"📺 Main stream: {camera.get_rtsp_url('main')}")
    print(f"📱 Sub stream: {camera.get_rtsp_url('sub')}")

    return camera


# Test
if __name__ == "__main__":
    print("📹 EZVIZ Integration Test\n")

    print("🔧 EZVIZ Husky Air Quick Setup\n")

    # Interactive setup
    camera = setup_husky_air()

    print("\n🎬 Test: Start sub stream...")
    if camera.start_stream("sub"):
        print("✅ Stream gestart!")

        import time
        time.sleep(3)

        print("\n📸 Test: Snapshot...")
        snapshot = camera.get_snapshot("sub")
        print(f"✅ Snapshot: {snapshot}")

        camera.stop_stream("sub")
    else:
        print("❌ Stream start gefaald")
        print("💡 Check:")
        print("   - IP adres correct?")
        print("   - Camera aan?")
        print("   - Netwerk bereikbaar?")

    print("\n✅ EZVIZ integration test compleet!")
