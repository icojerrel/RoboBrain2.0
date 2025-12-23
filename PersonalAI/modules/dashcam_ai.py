"""
PersonalAI Smart Dashcam
AI-powered dashcam upgrade met RoboBrain 2.0

Features:
- Continuous recording met event-triggered clips
- License plate capture van omliggende voertuigen
- Traffic sign recognition
- Collision/incident detection
- Lane departure warnings
- Driver monitoring (drowsiness detection)
- Parking mode surveillance
- GPS tracking met speed logging
"""

import sys
import cv2
import logging
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import queue

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.brain import get_brain
from modules.license_plate_ai import get_license_plate_ai
from modules.face_recognition_ai import get_face_recognition

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Dashcam event types"""
    COLLISION = "collision"
    NEAR_MISS = "near_miss"
    HARD_BRAKE = "hard_brake"
    RAPID_ACCELERATION = "rapid_acceleration"
    TRAFFIC_VIOLATION = "traffic_violation"
    TRAFFIC_SIGN = "traffic_sign"
    LANE_DEPARTURE = "lane_departure"
    FORWARD_COLLISION_WARNING = "forward_collision_warning"
    DRIVER_DROWSY = "driver_drowsy"
    DRIVER_DISTRACTED = "driver_distracted"
    PARKING_MOTION = "parking_motion"
    LICENSE_PLATE_DETECTED = "license_plate_detected"
    SPEED_LIMIT = "speed_limit"
    CUSTOM = "custom"


class RecordingMode(Enum):
    """Recording modes"""
    CONTINUOUS = "continuous"
    EVENT_ONLY = "event_only"
    PARKING = "parking"
    OFF = "off"


@dataclass
class DashcamEvent:
    """Dashcam event"""
    event_type: EventType
    timestamp: datetime
    description: str
    severity: str  # "low", "medium", "high", "critical"
    confidence: float
    video_clip_path: Optional[str] = None
    snapshot_path: Optional[str] = None
    location: Optional[Dict] = None  # GPS coords
    speed: Optional[float] = None  # km/h
    metadata: Optional[Dict] = None


@dataclass
class GPSData:
    """GPS location data"""
    latitude: float
    longitude: float
    speed: float  # km/h
    heading: float  # degrees
    altitude: float  # meters
    timestamp: datetime


class DashcamAI:
    """
    AI-powered dashcam met RoboBrain 2.0

    Combineert camera monitoring, vision AI, license plate reading
    voor complete driving assistance en incident recording.
    """

    def __init__(self,
                 front_camera_source: str = "0",
                 rear_camera_source: Optional[str] = None,
                 driver_camera_source: Optional[str] = None):
        """
        Initialize dashcam

        Args:
            front_camera_source: Front camera (webcam 0, RTSP URL, etc.)
            rear_camera_source: Optional rear camera
            driver_camera_source: Optional driver-facing camera
        """
        self.brain = get_brain()
        self.license_plate_ai = get_license_plate_ai()

        # Camera sources
        self.front_camera_source = front_camera_source
        self.rear_camera_source = rear_camera_source
        self.driver_camera_source = driver_camera_source

        # OpenCV captures
        self.front_capture = None
        self.rear_capture = None
        self.driver_capture = None

        # Recording state
        self.recording_mode = RecordingMode.CONTINUOUS
        self.is_recording = False
        self.is_monitoring = False

        # Video writers
        self.video_writers = {}
        self.current_clip_start = None

        # Event system
        self.events: List[DashcamEvent] = []
        self.event_callbacks: List[Callable] = []

        # Circular buffer for continuous recording
        self.buffer_duration = 30  # seconds before event
        self.clip_duration_after = 10  # seconds after event
        self.frame_buffer = queue.Queue(maxsize=900)  # 30 fps * 30 sec

        # Storage paths
        self.clips_dir = config.DATA_DIR / "dashcam" / "clips"
        self.snapshots_dir = config.DATA_DIR / "dashcam" / "snapshots"
        self.events_file = config.DATA_DIR / "dashcam" / "events.json"

        self.clips_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        # Load events history
        self.events = self._load_events()

        # GPS data (can be integrated with real GPS device)
        self.current_gps: Optional[GPSData] = None
        self.gps_enabled = False

        # Analysis settings
        self.analysis_interval = 2.0  # Analyze every 2 seconds
        self.last_analysis_time = 0

        # Threading
        self.monitor_thread = None
        self.recording_thread = None
        self.stop_event = threading.Event()

        # Driver monitoring
        self.driver_monitoring_enabled = driver_camera_source is not None
        self.last_driver_check = 0
        self.driver_check_interval = 5.0  # Check driver every 5 sec

        logger.info("🚗 Dashcam AI geïnitialiseerd")

    def _load_events(self) -> List[DashcamEvent]:
        """Laad event history"""
        if self.events_file.exists():
            try:
                with open(self.events_file, 'r') as f:
                    data = json.load(f)
                    return [
                        DashcamEvent(
                            event_type=EventType(e['event_type']),
                            timestamp=datetime.fromisoformat(e['timestamp']),
                            description=e['description'],
                            severity=e['severity'],
                            confidence=e['confidence'],
                            video_clip_path=e.get('video_clip_path'),
                            snapshot_path=e.get('snapshot_path'),
                            location=e.get('location'),
                            speed=e.get('speed'),
                            metadata=e.get('metadata')
                        )
                        for e in data
                    ]
            except Exception as e:
                logger.warning(f"Kon events niet laden: {e}")
        return []

    def _save_events(self):
        """Sla events op"""
        try:
            data = [
                {
                    'event_type': e.event_type.value,
                    'timestamp': e.timestamp.isoformat(),
                    'description': e.description,
                    'severity': e.severity,
                    'confidence': e.confidence,
                    'video_clip_path': e.video_clip_path,
                    'snapshot_path': e.snapshot_path,
                    'location': e.location,
                    'speed': e.speed,
                    'metadata': e.metadata
                }
                for e in self.events[-1000:]  # Keep last 1000 events
            ]

            with open(self.events_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Kon events niet opslaan: {e}")

    def start_cameras(self):
        """Start camera captures"""
        try:
            # Front camera (required)
            if isinstance(self.front_camera_source, str) and self.front_camera_source.isdigit():
                self.front_capture = cv2.VideoCapture(int(self.front_camera_source))
            else:
                self.front_capture = cv2.VideoCapture(self.front_camera_source)

            if not self.front_capture.isOpened():
                raise Exception("Kan front camera niet openen")

            # Rear camera (optional)
            if self.rear_camera_source:
                if isinstance(self.rear_camera_source, str) and self.rear_camera_source.isdigit():
                    self.rear_capture = cv2.VideoCapture(int(self.rear_camera_source))
                else:
                    self.rear_capture = cv2.VideoCapture(self.rear_camera_source)

            # Driver camera (optional)
            if self.driver_camera_source:
                if isinstance(self.driver_camera_source, str) and self.driver_camera_source.isdigit():
                    self.driver_capture = cv2.VideoCapture(int(self.driver_camera_source))
                else:
                    self.driver_capture = cv2.VideoCapture(self.driver_camera_source)

            logger.info("✅ Cameras gestart")
            return True

        except Exception as e:
            logger.error(f"❌ Camera start error: {e}")
            return False

    def stop_cameras(self):
        """Stop alle cameras"""
        if self.front_capture:
            self.front_capture.release()
        if self.rear_capture:
            self.rear_capture.release()
        if self.driver_capture:
            self.driver_capture.release()

        logger.info("🛑 Cameras gestopt")

    def start_recording(self, mode: RecordingMode = RecordingMode.CONTINUOUS):
        """Start recording"""
        self.recording_mode = mode
        self.is_recording = True

        if not self.start_cameras():
            return False

        # Start recording thread
        self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.recording_thread.start()

        logger.info(f"🎥 Recording gestart: {mode.value}")
        return True

    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        self.stop_event.set()

        if self.recording_thread:
            self.recording_thread.join(timeout=5.0)

        self.stop_cameras()
        self._save_events()

        logger.info("⏹️ Recording gestopt")

    def start_monitoring(self):
        """Start AI monitoring (zonder continuous recording)"""
        self.is_monitoring = True

        if not self.start_cameras():
            return False

        # Start monitor thread
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("👁️ AI monitoring gestart")
        return True

    def stop_monitoring(self):
        """Stop AI monitoring"""
        self.is_monitoring = False
        self.stop_event.set()

        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

        self.stop_cameras()
        self._save_events()

        logger.info("⏸️ Monitoring gestopt")

    def _recording_loop(self):
        """Main recording loop"""
        fps = 30
        frame_time = 1.0 / fps

        while self.is_recording and not self.stop_event.is_set():
            try:
                start = time.time()

                # Capture front frame
                if self.front_capture:
                    ret, frame = self.front_capture.read()
                    if ret:
                        # Add to circular buffer
                        if self.frame_buffer.full():
                            self.frame_buffer.get()
                        self.frame_buffer.put((time.time(), frame.copy()))

                        # Periodic AI analysis
                        if time.time() - self.last_analysis_time > self.analysis_interval:
                            self._analyze_scene(frame)
                            self.last_analysis_time = time.time()

                # Driver monitoring check
                if (self.driver_monitoring_enabled and
                    time.time() - self.last_driver_check > self.driver_check_interval):
                    self._check_driver()
                    self.last_driver_check = time.time()

                # Sleep to maintain FPS
                elapsed = time.time() - start
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)

            except Exception as e:
                logger.error(f"Recording loop error: {e}")
                time.sleep(1.0)

    def _monitoring_loop(self):
        """Monitoring loop (zonder recording)"""
        while self.is_monitoring and not self.stop_event.is_set():
            try:
                # Capture and analyze
                if self.front_capture:
                    ret, frame = self.front_capture.read()
                    if ret:
                        self._analyze_scene(frame)

                # Driver check
                if self.driver_monitoring_enabled:
                    self._check_driver()

                time.sleep(self.analysis_interval)

            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(2.0)

    def _analyze_scene(self, frame):
        """Analyseer scene met RoboBrain"""
        try:
            # Save temp frame
            temp_path = config.CACHE_DIR / f"dashcam_frame_{int(time.time())}.jpg"
            cv2.imwrite(str(temp_path), frame)

            # Analyze with RoboBrain
            prompt = """
            Analyseer deze dashcam view voor veiligheid:

            1. Zie je gevaarlijke situaties? (voetgangers, obstakels, etc.)
            2. Verkeersborden zichtbaar?
            3. Afstand tot voertuig vooruit (ver/gemiddeld/dichtbij)?
            4. Rijstrook - blijft auto in eigen baan?
            5. Ongebruikelijke activiteit?

            Wees kort en direct. Focus op veiligheid.
            """

            result = self.brain.analyze(
                image=str(temp_path),
                prompt=prompt,
                task="general",
                thinking=True
            )

            answer = result.get('answer', '').lower()

            # Detect events from analysis
            self._detect_events_from_analysis(answer, frame, temp_path)

            # Cleanup
            if temp_path.exists():
                temp_path.unlink()

        except Exception as e:
            logger.error(f"Scene analysis error: {e}")

    def _detect_events_from_analysis(self, analysis: str, frame, image_path: Path):
        """Detecteer events uit AI analyse"""

        # Collision/near-miss detection
        danger_keywords = ['gevaar', 'collision', 'botsing', 'crash', 'near miss', 'bijna']
        if any(kw in analysis for kw in danger_keywords):
            self._trigger_event(
                EventType.NEAR_MISS,
                "Mogelijk gevaarlijke situatie gedetecteerd",
                severity="high",
                confidence=0.8,
                frame=frame
            )

        # Traffic sign detection
        if 'verkeersbord' in analysis or 'sign' in analysis or 'snelheidslimiet' in analysis:
            self._trigger_event(
                EventType.TRAFFIC_SIGN,
                f"Verkeersbord gedetecteerd: {analysis[:100]}",
                severity="low",
                confidence=0.7
            )

        # Lane departure
        if 'baan' in analysis or 'rijstrook' in analysis:
            if 'uit' in analysis or 'buiten' in analysis or 'verlaat' in analysis:
                self._trigger_event(
                    EventType.LANE_DEPARTURE,
                    "Mogelijk rijstrook verlaten",
                    severity="medium",
                    confidence=0.6,
                    frame=frame
                )

        # Forward collision warning
        if 'dichtbij' in analysis or 'close' in analysis or 'te dicht' in analysis:
            self._trigger_event(
                EventType.FORWARD_COLLISION_WARNING,
                "Voertuig te dichtbij - verhoog afstand",
                severity="medium",
                confidence=0.7
            )

        # License plate detection in frame
        try:
            plates = self.license_plate_ai.detect_plates(str(image_path))
            if plates:
                for plate in plates:
                    self._trigger_event(
                        EventType.LICENSE_PLATE_DETECTED,
                        f"Kenteken gedetecteerd: {plate.plate_number}",
                        severity="low",
                        confidence=plate.confidence,
                        metadata={'plate': plate.plate_number}
                    )
        except Exception as e:
            logger.debug(f"License plate detection error: {e}")

    def _check_driver(self):
        """Check driver status (drowsiness, distraction)"""
        if not self.driver_capture:
            return

        try:
            ret, frame = self.driver_capture.read()
            if not ret:
                return

            # Save temp frame
            temp_path = config.CACHE_DIR / f"driver_frame_{int(time.time())}.jpg"
            cv2.imwrite(str(temp_path), frame)

            # Analyze driver
            prompt = """
            Analyseer de bestuurder:

            1. Zijn de ogen open of gesloten?
            2. Kijkt de bestuurder naar de weg?
            3. Tekenen van vermoeidheid?
            4. Is de bestuurder afgeleid? (telefoon, etc.)

            Kort antwoord gericht op veiligheid.
            """

            result = self.brain.analyze(
                image=str(temp_path),
                prompt=prompt,
                task="general",
                thinking=False
            )

            answer = result.get('answer', '').lower()

            # Detect driver issues
            if 'gesloten' in answer or 'dicht' in answer or 'moe' in answer:
                self._trigger_event(
                    EventType.DRIVER_DROWSY,
                    "⚠️ WAARSCHUWING: Bestuurder lijkt vermoeid!",
                    severity="critical",
                    confidence=0.8,
                    frame=frame
                )

            if 'afgeleid' in answer or 'telefoon' in answer or 'niet naar weg' in answer:
                self._trigger_event(
                    EventType.DRIVER_DISTRACTED,
                    "⚠️ WAARSCHUWING: Bestuurder is afgeleid!",
                    severity="high",
                    confidence=0.75,
                    frame=frame
                )

            # Cleanup
            if temp_path.exists():
                temp_path.unlink()

        except Exception as e:
            logger.error(f"Driver check error: {e}")

    def _trigger_event(self,
                       event_type: EventType,
                       description: str,
                       severity: str = "medium",
                       confidence: float = 0.7,
                       frame=None,
                       metadata: Dict = None):
        """Trigger een dashcam event"""

        # Save snapshot if frame provided
        snapshot_path = None
        if frame is not None:
            snapshot_path = self.snapshots_dir / f"{event_type.value}_{int(time.time())}.jpg"
            cv2.imwrite(str(snapshot_path), frame)

        # Create event
        event = DashcamEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            description=description,
            severity=severity,
            confidence=confidence,
            snapshot_path=str(snapshot_path) if snapshot_path else None,
            location=self._get_current_location(),
            speed=self.current_gps.speed if self.current_gps else None,
            metadata=metadata
        )

        self.events.append(event)

        # Save video clip if critical/high severity
        if severity in ['critical', 'high'] and self.is_recording:
            self._save_event_clip(event)

        # Call event callbacks
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Event callback error: {e}")

        logger.warning(f"🚨 Event: {event_type.value} - {description}")

        # Auto-save events
        self._save_events()

    def _save_event_clip(self, event: DashcamEvent):
        """Sla video clip van event op (buffer + after)"""
        try:
            clip_path = self.clips_dir / f"{event.event_type.value}_{int(time.time())}.mp4"

            # Get frames from buffer
            frames = list(self.frame_buffer.queue)

            if not frames:
                return

            # Setup video writer
            height, width = frames[0][1].shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(str(clip_path), fourcc, 30, (width, height))

            # Write buffered frames
            for timestamp, frame in frames:
                writer.write(frame)

            # Continue recording for clip_duration_after seconds
            # (This would need integration with recording loop)

            writer.release()

            event.video_clip_path = str(clip_path)
            logger.info(f"💾 Event clip opgeslagen: {clip_path}")

        except Exception as e:
            logger.error(f"Clip save error: {e}")

    def _get_current_location(self) -> Optional[Dict]:
        """Krijg huidige GPS locatie"""
        if self.current_gps:
            return {
                'latitude': self.current_gps.latitude,
                'longitude': self.current_gps.longitude,
                'speed': self.current_gps.speed,
                'heading': self.current_gps.heading
            }
        return None

    def update_gps(self, latitude: float, longitude: float,
                   speed: float, heading: float = 0, altitude: float = 0):
        """Update GPS data (call from external GPS source)"""
        self.current_gps = GPSData(
            latitude=latitude,
            longitude=longitude,
            speed=speed,
            heading=heading,
            altitude=altitude,
            timestamp=datetime.now()
        )
        self.gps_enabled = True

    def add_event_callback(self, callback: Callable):
        """Voeg event callback toe"""
        self.event_callbacks.append(callback)

    def get_events(self,
                   event_type: Optional[EventType] = None,
                   severity: Optional[str] = None,
                   limit: int = 50) -> List[DashcamEvent]:
        """Krijg events met filters"""
        filtered = self.events

        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]

        if severity:
            filtered = [e for e in filtered if e.severity == severity]

        return filtered[-limit:]

    def get_statistics(self) -> Dict:
        """Krijg dashcam statistieken"""
        total_events = len(self.events)

        by_type = {}
        for event in self.events:
            by_type[event.event_type.value] = by_type.get(event.event_type.value, 0) + 1

        by_severity = {}
        for event in self.events:
            by_severity[event.severity] = by_severity.get(event.severity, 0) + 1

        return {
            'total_events': total_events,
            'events_by_type': by_type,
            'events_by_severity': by_severity,
            'recording_mode': self.recording_mode.value,
            'is_recording': self.is_recording,
            'is_monitoring': self.is_monitoring,
            'gps_enabled': self.gps_enabled,
            'driver_monitoring': self.driver_monitoring_enabled
        }

    def export_events(self, filepath: str, format: str = "csv"):
        """Exporteer events naar file"""
        import csv

        if format == "csv":
            with open(filepath, 'w', newline='') as f:
                if not self.events:
                    return

                fieldnames = ['timestamp', 'event_type', 'severity', 'description',
                             'confidence', 'speed', 'location', 'clip_path']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for event in self.events:
                    writer.writerow({
                        'timestamp': event.timestamp.isoformat(),
                        'event_type': event.event_type.value,
                        'severity': event.severity,
                        'description': event.description,
                        'confidence': event.confidence,
                        'speed': event.speed or '',
                        'location': str(event.location) if event.location else '',
                        'clip_path': event.video_clip_path or ''
                    })

            logger.info(f"📊 Events geëxporteerd naar {filepath}")

        elif format == "json":
            self._save_events()
            import shutil
            shutil.copy(self.events_file, filepath)
            logger.info(f"📊 Events geëxporteerd naar {filepath}")


# Singleton
_dashcam: Optional[DashcamAI] = None


def get_dashcam(front_camera: str = "0",
                rear_camera: Optional[str] = None,
                driver_camera: Optional[str] = None) -> DashcamAI:
    """Krijg dashcam AI (singleton)"""
    global _dashcam
    if _dashcam is None:
        _dashcam = DashcamAI(front_camera, rear_camera, driver_camera)
    return _dashcam


# Test
if __name__ == "__main__":
    print("🚗 Dashcam AI Test\n")

    # Initialize dashcam
    dashcam = get_dashcam(front_camera="0")

    # Setup event callback
    def on_event(event: DashcamEvent):
        print(f"\n🚨 EVENT: {event.event_type.value}")
        print(f"   Severity: {event.severity}")
        print(f"   Description: {event.description}")
        if event.location:
            print(f"   Location: {event.location}")

    dashcam.add_event_callback(on_event)

    print("✅ Dashcam gereed!")
    print(f"\n📊 Stats: {dashcam.get_statistics()}")

    print("\n💡 Gebruik:")
    print("  dashcam.start_recording(RecordingMode.CONTINUOUS)")
    print("  dashcam.start_monitoring()  # Zonder opname")
    print("  dashcam.update_gps(lat, lon, speed, heading)")
    print("  dashcam.get_events(event_type=EventType.COLLISION)")
    print("  dashcam.export_events('incidents.csv')")
