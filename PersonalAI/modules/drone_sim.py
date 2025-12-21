"""
PersonalAI Drone Simulator
Veilige drone simulator voor vision-based autonomous control
"""

import sys
import time
import math
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json

import numpy as np
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("⚠️ PIL niet gevonden. Installeer met: pip install Pillow")

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.brain import get_brain

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class DroneState(Enum):
    """Drone status"""
    IDLE = "idle"
    ARMED = "armed"
    FLYING = "flying"
    LANDING = "landing"
    EMERGENCY = "emergency"
    CRASHED = "crashed"


@dataclass
class Position:
    """3D positie"""
    x: float = 0.0  # meters
    y: float = 0.0  # meters
    z: float = 0.0  # meters (hoogte)

    def distance_to(self, other: 'Position') -> float:
        """Bereken afstand tot andere positie"""
        return math.sqrt(
            (self.x - other.x)**2 +
            (self.y - other.y)**2 +
            (self.z - other.z)**2
        )

    def to_dict(self) -> Dict:
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass
class Velocity:
    """3D snelheid"""
    vx: float = 0.0  # m/s
    vy: float = 0.0  # m/s
    vz: float = 0.0  # m/s (vertical)

    def magnitude(self) -> float:
        """Totale snelheid"""
        return math.sqrt(self.vx**2 + self.vy**2 + self.vz**2)


@dataclass
class Obstacle:
    """Obstakel in de omgeving"""
    position: Position
    radius: float
    name: str


class DroneSimulator:
    """
    Simpele maar realistische drone simulator
    Voor vision-based autonomous control testing
    """

    def __init__(self, world_size: Tuple[float, float] = (100, 100)):
        """
        Args:
            world_size: (width, height) van de wereld in meters
        """
        # Wereld parameters
        self.world_width = world_size[0]
        self.world_height = world_size[1]
        self.max_altitude = 50.0  # max hoogte in meters

        # Drone state
        self.state = DroneState.IDLE
        self.position = Position(x=50.0, y=50.0, z=0.0)  # Start centrum
        self.velocity = Velocity()
        self.yaw = 0.0  # rotatie (graden)

        # Drone specs (DJI-achtig)
        self.max_speed = 15.0  # m/s
        self.max_vertical_speed = 5.0  # m/s
        self.max_yaw_rate = 100.0  # deg/s
        self.battery = 100.0  # percentage
        self.battery_drain_rate = 0.1  # % per seconde bij hoveren

        # Obstacles/objects in wereld
        self.obstacles: List[Obstacle] = []
        self._create_default_world()

        # Missie
        self.waypoints: List[Position] = []
        self.current_waypoint_idx = 0

        # Safety
        self.safety_distance = 2.0  # meters
        self.emergency_stop = False

        # Telemetrie geschiedenis
        self.telemetry_history = []

        # Tijdstap voor simulatie
        self.dt = 0.1  # 10 Hz update
        self.sim_time = 0.0

        logger.info("🚁 Drone Simulator geïnitialiseerd")
        logger.info(f"   Wereld: {self.world_width}x{self.world_height}m")
        logger.info(f"   Start positie: {self.position.to_dict()}")

    def _create_default_world(self):
        """Maak een standaard testwereld met obstakels"""
        self.obstacles = [
            Obstacle(Position(30, 30, 0), radius=5.0, name="Boom 1"),
            Obstacle(Position(70, 70, 0), radius=5.0, name="Boom 2"),
            Obstacle(Position(50, 80, 0), radius=3.0, name="Boom 3"),
            Obstacle(Position(20, 60, 0), radius=4.0, name="Gebouw"),
            Obstacle(Position(80, 40, 0), radius=6.0, name="Toren"),
        ]

    def arm(self) -> bool:
        """Arm de drone (klaar voor vlucht)"""
        if self.state == DroneState.IDLE:
            self.state = DroneState.ARMED
            logger.info("✅ Drone armed en klaar voor takeoff")
            return True
        return False

    def disarm(self) -> bool:
        """Disarm de drone"""
        if self.position.z < 0.1:  # moet op de grond zijn
            self.state = DroneState.IDLE
            logger.info("🔓 Drone disarmed")
            return True
        return False

    def takeoff(self, altitude: float = 10.0) -> bool:
        """
        Takeoff naar specifieke hoogte

        Args:
            altitude: Doel hoogte in meters
        """
        if self.state != DroneState.ARMED:
            logger.warning("⚠️ Drone moet eerst armed zijn!")
            return False

        if altitude > self.max_altitude:
            logger.warning(f"⚠️ Max altitude is {self.max_altitude}m")
            return False

        self.state = DroneState.FLYING
        logger.info(f"🚁 Takeoff naar {altitude}m...")

        # Simuleer takeoff
        while self.position.z < altitude:
            self.position.z += self.max_vertical_speed * self.dt
            self.battery -= self.battery_drain_rate * 2 * self.dt  # Extra drain bij climb
            self._update_telemetry()
            time.sleep(self.dt / 10)  # Versnelde simulatie

        logger.info(f"✅ Hovering op {self.position.z:.1f}m")
        return True

    def land(self) -> bool:
        """Land de drone"""
        if self.state != DroneState.FLYING:
            return False

        self.state = DroneState.LANDING
        logger.info("🛬 Landing...")

        # Simuleer landing
        while self.position.z > 0.1:
            self.position.z -= self.max_vertical_speed * 0.5 * self.dt
            self.position.z = max(0, self.position.z)
            self.battery -= self.battery_drain_rate * self.dt
            self._update_telemetry()
            time.sleep(self.dt / 10)

        self.position.z = 0.0
        self.velocity = Velocity()
        self.state = DroneState.ARMED
        logger.info("✅ Landed")
        return True

    def move_to(self, target: Position, speed: float = None) -> bool:
        """
        Vlieg naar target positie

        Args:
            target: Doel positie
            speed: Snelheid in m/s (None = max speed)
        """
        if self.state != DroneState.FLYING:
            logger.warning("⚠️ Drone moet flying zijn!")
            return False

        speed = speed or self.max_speed * 0.7  # 70% van max voor veiligheid

        logger.info(f"🎯 Vliegen naar {target.to_dict()}")

        # Check voor obstakels
        if not self._is_path_safe(self.position, target):
            logger.error("❌ Pad heeft obstakels! Emergency stop.")
            self.emergency_stop = True
            return False

        # Bereken richting
        distance = self.position.distance_to(target)

        while distance > 1.0:  # Stop binnen 1 meter
            if self.emergency_stop:
                logger.error("🛑 Emergency stop activated!")
                self.hover()
                return False

            # Bereken richting vector
            dx = target.x - self.position.x
            dy = target.y - self.position.y
            dz = target.z - self.position.z

            # Normaliseer
            norm = math.sqrt(dx**2 + dy**2 + dz**2)
            if norm > 0:
                dx /= norm
                dy /= norm
                dz /= norm

            # Update velocity
            self.velocity.vx = dx * speed
            self.velocity.vy = dy * speed
            self.velocity.vz = dz * min(speed, self.max_vertical_speed)

            # Update positie
            self.position.x += self.velocity.vx * self.dt
            self.position.y += self.velocity.vy * self.dt
            self.position.z += self.velocity.vz * self.dt

            # Clamp binnen grenzen
            self._enforce_boundaries()

            # Battery drain
            self.battery -= self.battery_drain_rate * (1 + self.velocity.magnitude() / self.max_speed) * self.dt

            # Check battery
            if self.battery < 20:
                logger.warning("⚠️ Low battery! Auto-landing...")
                self.land()
                return False

            # Update telemetry
            self._update_telemetry()

            # Recalculate distance
            distance = self.position.distance_to(target)

            time.sleep(self.dt / 10)  # Versnelde sim

        # Stop bij waypoint
        self.hover()
        logger.info(f"✅ Waypoint bereikt op {self.position.to_dict()}")
        return True

    def hover(self):
        """Hover op huidige positie"""
        self.velocity = Velocity()

    def _is_path_safe(self, start: Position, end: Position) -> bool:
        """Check of pad vrij is van obstakels"""
        for obstacle in self.obstacles:
            # Simpele collision detection
            # Check of lijn tussen start en end te dicht bij obstakel komt
            dist_to_obstacle = self._distance_point_to_line(
                obstacle.position, start, end
            )

            if dist_to_obstacle < (obstacle.radius + self.safety_distance):
                logger.warning(f"⚠️ Obstakel '{obstacle.name}' in de weg!")
                return False

        return True

    def _distance_point_to_line(self, point: Position, line_start: Position,
                                line_end: Position) -> float:
        """Bereken afstand van punt tot lijn"""
        # Vector van start naar end
        dx = line_end.x - line_start.x
        dy = line_end.y - line_start.y

        if dx == 0 and dy == 0:
            return point.distance_to(line_start)

        # Parameter langs de lijn
        t = max(0, min(1, (
            (point.x - line_start.x) * dx +
            (point.y - line_start.y) * dy
        ) / (dx**2 + dy**2)))

        # Dichtstbijzijnde punt op lijn
        closest_x = line_start.x + t * dx
        closest_y = line_start.y + t * dy

        # Afstand
        return math.sqrt(
            (point.x - closest_x)**2 +
            (point.y - closest_y)**2
        )

    def _enforce_boundaries(self):
        """Houd drone binnen wereld grenzen"""
        self.position.x = max(0, min(self.world_width, self.position.x))
        self.position.y = max(0, min(self.world_height, self.position.y))
        self.position.z = max(0, min(self.max_altitude, self.position.z))

    def _update_telemetry(self):
        """Update telemetrie geschiedenis"""
        telemetry = {
            'time': self.sim_time,
            'position': self.position.to_dict(),
            'velocity': self.velocity.magnitude(),
            'battery': self.battery,
            'state': self.state.value
        }
        self.telemetry_history.append(telemetry)
        self.sim_time += self.dt

    def get_status(self) -> Dict:
        """Krijg huidige drone status"""
        return {
            'state': self.state.value,
            'position': self.position.to_dict(),
            'velocity': {
                'vx': self.velocity.vx,
                'vy': self.velocity.vy,
                'vz': self.velocity.vz,
                'magnitude': self.velocity.magnitude()
            },
            'yaw': self.yaw,
            'battery': round(self.battery, 1),
            'altitude': round(self.position.z, 2),
            'sim_time': round(self.sim_time, 1)
        }

    def render_world(self, output_path: str = None) -> Image.Image:
        """
        Render een top-down view van de wereld

        Args:
            output_path: Pad om afbeelding op te slaan

        Returns:
            PIL Image
        """
        # Maak canvas
        scale = 10  # pixels per meter
        width = int(self.world_width * scale)
        height = int(self.world_height * scale)

        img = Image.new('RGB', (width, height), color='lightgreen')
        draw = ImageDraw.Draw(img)

        # Teken obstakels
        for obstacle in self.obstacles:
            x = int(obstacle.position.x * scale)
            y = int(obstacle.position.y * scale)
            r = int(obstacle.radius * scale)

            # Obstakel
            draw.ellipse([x-r, y-r, x+r, y+r], fill='brown', outline='black')

            # Safety zone
            safety_r = int((obstacle.radius + self.safety_distance) * scale)
            draw.ellipse([x-safety_r, y-safety_r, x+safety_r, y+safety_r],
                        outline='red', width=2)

        # Teken waypoints
        for i, wp in enumerate(self.waypoints):
            x = int(wp.x * scale)
            y = int(wp.y * scale)
            draw.ellipse([x-5, y-5, x+5, y+5], fill='blue', outline='white')
            draw.text((x+10, y), f"WP{i}", fill='blue')

        # Teken drone
        x = int(self.position.x * scale)
        y = int(self.position.y * scale)

        # Drone body
        draw.ellipse([x-10, y-10, x+10, y+10], fill='red', outline='black', width=2)

        # Direction indicator (yaw)
        arrow_len = 15
        arrow_x = x + int(arrow_len * math.cos(math.radians(self.yaw)))
        arrow_y = y + int(arrow_len * math.sin(math.radians(self.yaw)))
        draw.line([x, y, arrow_x, arrow_y], fill='yellow', width=3)

        # Info text
        info_text = f"Alt: {self.position.z:.1f}m | Battery: {self.battery:.0f}% | {self.state.value}"
        draw.text((10, 10), info_text, fill='black')

        # Save als gevraagd
        if output_path:
            img.save(output_path)
            logger.info(f"💾 Wereld gerenderd naar {output_path}")

        return img

    def add_waypoint(self, position: Position):
        """Voeg waypoint toe aan missie"""
        self.waypoints.append(position)
        logger.info(f"📍 Waypoint toegevoegd: {position.to_dict()}")

    def execute_mission(self) -> bool:
        """Voer volledige missie uit (alle waypoints)"""
        if not self.waypoints:
            logger.warning("⚠️ Geen waypoints geprogrammeerd!")
            return False

        logger.info(f"🎯 Start missie met {len(self.waypoints)} waypoints")

        for i, wp in enumerate(self.waypoints):
            logger.info(f"📍 Waypoint {i+1}/{len(self.waypoints)}")
            if not self.move_to(wp):
                logger.error(f"❌ Missie gefaald bij waypoint {i+1}")
                return False

        logger.info("✅ Missie compleet!")
        return True

    def save_telemetry(self, filename: str):
        """Sla telemetrie op naar JSON"""
        filepath = config.DATA_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(self.telemetry_history, f, indent=2)
        logger.info(f"💾 Telemetrie opgeslagen: {filepath}")


# Singleton instance
_drone_sim: Optional[DroneSimulator] = None

def get_drone_simulator() -> DroneSimulator:
    """Krijg of maak drone simulator (singleton)"""
    global _drone_sim
    if _drone_sim is None:
        _drone_sim = DroneSimulator()
    return _drone_sim


# Test code
if __name__ == "__main__":
    print("🚁 Drone Simulator Test\n")

    # Maak simulator
    drone = DroneSimulator(world_size=(100, 100))

    # Test vlucht
    print("Test Vlucht:")
    drone.arm()
    drone.takeoff(altitude=15.0)

    # Voeg waypoints toe
    drone.add_waypoint(Position(30, 30, 15))
    drone.add_waypoint(Position(70, 70, 15))
    drone.add_waypoint(Position(50, 50, 15))

    # Render wereld
    drone.render_world("test_world.png")

    # Voer missie uit
    drone.execute_mission()

    # Land
    drone.land()
    drone.disarm()

    # Status
    print(f"\n✅ Status: {drone.get_status()}")

    # Save telemetry
    drone.save_telemetry("test_flight.json")

    print("\n🎉 Simulator test compleet!")
