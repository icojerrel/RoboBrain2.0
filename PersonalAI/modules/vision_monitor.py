"""
PersonalAI Vision Monitor
Real-time AI vision analysis voor camera feeds
Met event detection, object tracking en alerts
"""

import sys
import time
import threading
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.brain import get_brain
from modules.camera_monitor import get_camera_manager, CameraConfig, CameraType

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event types voor detection"""
    MOTION = "motion"
    PERSON_DETECTED = "person_detected"
    OBJECT_DETECTED = "object_detected"
    UNUSUAL_ACTIVITY = "unusual_activity"
    INTRUSION = "intrusion"
    CUSTOM = "custom"


@dataclass
class VisionEvent:
    """Vision event data"""
    event_type: EventType
    camera_name: str
    timestamp: datetime
    confidence: float
    description: str
    image_path: str
    metadata: Dict


class VisionMonitor:
    """
    AI-powered camera monitoring met RoboBrain 2.0
    Real-time scene understanding en event detection
    """

    def __init__(self):
        self.brain = get_brain()
        self.camera_manager = get_camera_manager()

        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Event callbacks
        self.event_callbacks: List[Callable] = []

        # Event history
        self.events: List[VisionEvent] = []
        self.max_events = 100

        # Analysis settings
        self.analysis_interval = 5.0  # Analyseer elke 5 seconden
        self.motion_threshold = 30  # Pixel difference threshold

        # Last analysis per camera
        self.last_analysis = {}
        self.last_frames = {}

        logger.info("👁️ Vision Monitor geïnitialiseerd")

    def start_monitoring(self, cameras: List[str] = None):
        """
        Start vision monitoring

        Args:
            cameras: Lijst van camera namen (None = alle cameras)
        """
        if self.is_monitoring:
            logger.warning("Monitoring is al actief")
            return

        self.is_monitoring = True

        # Start camera streams
        if cameras is None:
            self.camera_manager.start_all()
        else:
            for cam_name in cameras:
                self.camera_manager.start_camera(cam_name)

        # Start monitoring thread
        def monitor_loop():
            logger.info("🔄 Vision monitoring gestart")

            while self.is_monitoring:
                try:
                    self._monitoring_cycle()
                    time.sleep(1.0)  # Check every second
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("✅ Vision monitoring actief")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)

        self.camera_manager.stop_all()

        logger.info("⏸️ Vision monitoring gestopt")

    def _monitoring_cycle(self):
        """Eén monitoring cycle voor alle camera's"""
        current_time = time.time()

        for cam_name, camera in self.camera_manager.cameras.items():
            if not camera.is_running:
                continue

            # Check of het tijd is voor analyse
            last_time = self.last_analysis.get(cam_name, 0)
            if current_time - last_time < self.analysis_interval:
                continue

            # Analyseer huidige frame
            self._analyze_camera(cam_name, camera)
            self.last_analysis[cam_name] = current_time

    def _analyze_camera(self, cam_name: str, camera):
        """Analyseer camera feed met AI"""
        # Get current frame
        frame = camera.last_frame
        if frame is None:
            return

        # Save frame voor analyse
        timestamp = int(time.time())
        frame_path = str(config.CACHE_DIR / f"frame_{cam_name}_{timestamp}.jpg")

        import cv2
        cv2.imwrite(frame_path, frame)

        # Motion detection (simpel)
        if cam_name in self.last_frames:
            motion_detected = self._detect_motion(
                self.last_frames[cam_name],
                frame
            )

            if motion_detected:
                self._trigger_event(
                    EventType.MOTION,
                    cam_name,
                    frame_path,
                    "Beweging gedetecteerd"
                )

        self.last_frames[cam_name] = frame

        # AI Scene analysis (periodiek)
        self._analyze_scene(cam_name, frame_path)

    def _detect_motion(self, prev_frame, curr_frame) -> bool:
        """Simpele motion detection"""
        import cv2
        import numpy as np

        # Convert to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        # Bereken verschil
        diff = cv2.absdiff(prev_gray, curr_gray)
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        # Count changed pixels
        changed_pixels = np.sum(thresh > 0)
        total_pixels = thresh.shape[0] * thresh.shape[1]

        change_percentage = (changed_pixels / total_pixels) * 100

        return change_percentage > self.motion_threshold

    def _analyze_scene(self, cam_name: str, image_path: str):
        """Analyseer scene met RoboBrain"""
        try:
            prompt = """
            Analyseer deze camera feed.

            Kijk naar:
            1. Zijn er mensen aanwezig?
            2. Welke objecten zijn zichtbaar?
            3. Is er ongebruikelijke activiteit?
            4. Algemene veiligheid en status
            5. Belangrijk om te weten

            Geef een kort, duidelijk antwoord.
            """

            result = self.brain.analyze(
                image=image_path,
                prompt=prompt,
                task="general",
                thinking=False  # Snel antwoord
            )

            answer = result.get('answer', '').lower()

            # Check for persons
            if any(word in answer for word in ['person', 'mensen', 'man', 'vrouw', 'persoon']):
                self._trigger_event(
                    EventType.PERSON_DETECTED,
                    cam_name,
                    image_path,
                    f"Persoon gedetecteerd: {result['answer']}"
                )

            # Check for unusual activity
            if any(word in answer for word in ['ongebruikelijk', 'vreemd', 'verdacht', 'unusual']):
                self._trigger_event(
                    EventType.UNUSUAL_ACTIVITY,
                    cam_name,
                    image_path,
                    f"Ongebruikelijke activiteit: {result['answer']}"
                )

        except Exception as e:
            logger.error(f"Scene analysis error: {e}")

    def _trigger_event(self, event_type: EventType, cam_name: str,
                      image_path: str, description: str,
                      confidence: float = 0.8, metadata: Dict = None):
        """Trigger een vision event"""
        event = VisionEvent(
            event_type=event_type,
            camera_name=cam_name,
            timestamp=datetime.now(),
            confidence=confidence,
            description=description,
            image_path=image_path,
            metadata=metadata or {}
        )

        # Add to history
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events.pop(0)

        # Log event
        logger.info(f"🚨 EVENT: {event_type.value} @ {cam_name}: {description}")

        # Call callbacks
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Event callback error: {e}")

    def add_event_callback(self, callback: Callable):
        """Voeg event callback toe"""
        self.event_callbacks.append(callback)

    def analyze_snapshot(self, cam_name: str, query: str = None) -> Dict:
        """
        Analyseer huidige camera snapshot

        Args:
            cam_name: Camera naam
            query: Specifieke vraag (optioneel)

        Returns:
            Analysis result
        """
        # Get snapshot
        snapshot = self.camera_manager.get_snapshot(cam_name)
        if not snapshot:
            return {'error': 'Geen snapshot beschikbaar'}

        # Default query
        if query is None:
            query = "Beschrijf wat je ziet in deze camera feed. Wees specifiek."

        # Analyze
        result = self.brain.analyze(
            image=snapshot,
            prompt=query,
            task="general",
            thinking=True
        )

        return result

    def find_object(self, cam_name: str, object_description: str) -> Dict:
        """
        Zoek object in camera view

        Args:
            cam_name: Camera naam
            object_description: Wat te zoeken

        Returns:
            Detection result met locatie
        """
        snapshot = self.camera_manager.get_snapshot(cam_name)
        if not snapshot:
            return {'error': 'Geen snapshot beschikbaar'}

        result = self.brain.find_objects(
            snapshot,
            object_description,
            plot=True
        )

        return result

    def count_people(self, cam_name: str) -> Dict:
        """
        Tel aantal mensen in camera view

        Args:
            cam_name: Camera naam

        Returns:
            Count result
        """
        snapshot = self.camera_manager.get_snapshot(cam_name)
        if not snapshot:
            return {'error': 'Geen snapshot beschikbaar'}

        prompt = "Hoeveel mensen zie je in deze camera feed? Tel nauwkeurig."

        result = self.brain.analyze(
            image=snapshot,
            prompt=prompt,
            task="general",
            thinking=True
        )

        return result

    def detect_changes(self, cam_name: str, reference_image: str) -> Dict:
        """
        Detecteer veranderingen t.o.v. referentie afbeelding

        Args:
            cam_name: Camera naam
            reference_image: Pad naar referentie afbeelding

        Returns:
            Change detection result
        """
        snapshot = self.camera_manager.get_snapshot(cam_name)
        if not snapshot:
            return {'error': 'Geen snapshot beschikbaar'}

        prompt = """
        Vergelijk deze twee camera views.

        Wat is er veranderd?
        - Nieuwe objecten?
        - Verwijderde objecten?
        - Verplaatste objecten?
        - Andere veranderingen?

        Wees specifiek over wat er anders is.
        """

        result = self.brain.compare_images(
            [reference_image, snapshot],
            prompt
        )

        return result

    def get_events(self, event_type: EventType = None,
                   camera_name: str = None,
                   limit: int = 10) -> List[VisionEvent]:
        """
        Krijg recente events

        Args:
            event_type: Filter op event type
            camera_name: Filter op camera
            limit: Max aantal events

        Returns:
            List van events
        """
        filtered = self.events

        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]

        if camera_name:
            filtered = [e for e in filtered if e.camera_name == camera_name]

        return filtered[-limit:]

    def get_status(self) -> Dict:
        """Krijg monitoring status"""
        return {
            'is_monitoring': self.is_monitoring,
            'cameras_active': len([c for c in self.camera_manager.cameras.values() if c.is_running]),
            'total_events': len(self.events),
            'analysis_interval': self.analysis_interval,
            'event_types': {
                etype.value: len([e for e in self.events if e.event_type == etype])
                for etype in EventType
            }
        }

    def save_events(self, filepath: str):
        """Sla events op naar JSON"""
        events_data = [
            {
                'type': e.event_type.value,
                'camera': e.camera_name,
                'timestamp': e.timestamp.isoformat(),
                'confidence': e.confidence,
                'description': e.description,
                'image': e.image_path
            }
            for e in self.events
        ]

        with open(filepath, 'w') as f:
            json.dump(events_data, f, indent=2)

        logger.info(f"💾 Events saved to {filepath}")


# Singleton
_vision_monitor: Optional[VisionMonitor] = None


def get_vision_monitor() -> VisionMonitor:
    """Krijg vision monitor (singleton)"""
    global _vision_monitor
    if _vision_monitor is None:
        _vision_monitor = VisionMonitor()
    return _vision_monitor


# Test
if __name__ == "__main__":
    print("👁️ Vision Monitor Test\n")

    monitor = get_vision_monitor()

    # Test event callback
    def on_event(event: VisionEvent):
        print(f"🚨 Event: {event.event_type.value} - {event.description}")

    monitor.add_event_callback(on_event)

    print("✅ Vision monitor gereed!")
    print("💡 Start monitoring met: monitor.start_monitoring()")
