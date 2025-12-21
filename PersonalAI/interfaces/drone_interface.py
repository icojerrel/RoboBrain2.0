"""
PersonalAI Drone Control Interface
Telegram commands voor drone simulator besturing
"""

import sys
import logging
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent))
import config
from modules.drone_sim import get_drone_simulator, Position, DroneState
from modules.drone_vision import get_drone_vision

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class DroneInterface:
    """
    User-friendly interface voor drone control
    Voor gebruik in Telegram bot en Web interface
    """

    def __init__(self):
        self.drone = get_drone_simulator()
        self.vision = get_drone_vision()
        logger.info("🎮 Drone Interface geïnitialiseerd")

    def cmd_status(self) -> str:
        """Krijg drone status (formatted)"""
        status = self.drone.get_status()

        return f"""
🚁 **Drone Status**

**State:** {status['state'].upper()}
**Position:** ({status['position']['x']:.1f}, {status['position']['y']:.1f}, {status['position']['z']:.1f})m
**Altitude:** {status['altitude']}m
**Battery:** {status['battery']}%
**Speed:** {status['velocity']['magnitude']:.1f} m/s
**Flight Time:** {status['sim_time']}s

**Velocity:**
• X: {status['velocity']['vx']:.1f} m/s
• Y: {status['velocity']['vy']:.1f} m/s
• Z: {status['velocity']['vz']:.1f} m/s
        """.strip()

    def cmd_arm(self) -> str:
        """Arm de drone"""
        if self.drone.arm():
            return "✅ Drone armed! Klaar voor takeoff.\n\nGebruik /drone_takeoff om op te stijgen."
        else:
            return f"❌ Kan niet armen. Current state: {self.drone.state.value}"

    def cmd_disarm(self) -> str:
        """Disarm de drone"""
        if self.drone.disarm():
            return "🔓 Drone disarmed."
        else:
            return "❌ Kan niet disarmen. Drone moet eerst landen!"

    def cmd_takeoff(self, altitude: float = 15.0) -> str:
        """Takeoff naar altitude"""
        if self.drone.takeoff(altitude):
            return f"🚁 Takeoff succesvol!\n\nHover op {altitude}m hoogte."
        else:
            return f"❌ Takeoff gefaald. State: {self.drone.state.value}"

    def cmd_land(self) -> str:
        """Land de drone"""
        if self.drone.land():
            return "🛬 Landing succesvol!\n\nDrone op de grond."
        else:
            return f"❌ Landing gefaald. State: {self.drone.state.value}"

    def cmd_goto(self, x: float, y: float, z: float = None) -> str:
        """Vlieg naar positie"""
        if z is None:
            z = self.drone.position.z  # Behoud huidige altitude

        target = Position(x, y, z)

        result = f"🎯 Vliegen naar ({x}, {y}, {z})...\n\n"

        if self.drone.move_to(target):
            result += "✅ Positie bereikt!"
        else:
            result += "❌ Vlucht gefaald!"

        return result

    def cmd_waypoint(self, x: float, y: float, z: float = 15.0) -> str:
        """Voeg waypoint toe"""
        self.drone.add_waypoint(Position(x, y, z))
        return f"📍 Waypoint toegevoegd: ({x}, {y}, {z})\n\nTotaal waypoints: {len(self.drone.waypoints)}"

    def cmd_clear_waypoints(self) -> str:
        """Wis alle waypoints"""
        count = len(self.drone.waypoints)
        self.drone.waypoints = []
        self.drone.current_waypoint_idx = 0
        return f"🗑️ {count} waypoints gewist."

    def cmd_mission(self) -> str:
        """Voer missie uit"""
        if not self.drone.waypoints:
            return "❌ Geen waypoints! Voeg eerst waypoints toe met /drone_waypoint"

        result = f"🚁 Start missie met {len(self.drone.waypoints)} waypoints...\n\n"

        if self.drone.execute_mission():
            result += "✅ Missie compleet!\n\nAlle waypoints bereikt."
        else:
            result += "❌ Missie gefaald!"

        return result

    def cmd_emergency(self) -> str:
        """Emergency stop + land"""
        self.drone.emergency_stop = True
        self.vision.emergency_land()
        return "🚨 EMERGENCY STOP!\n\nDrone geland in noodmodus."

    def cmd_render(self, output_path: str = None) -> str:
        """Render wereld view"""
        if output_path is None:
            output_path = str(config.CACHE_DIR / "drone_world.png")

        self.drone.render_world(output_path)
        return output_path  # Return path voor telegram photo upload

    def cmd_vision_analyze(self, image_path: str) -> str:
        """Analyseer drone camera view"""
        result = self.vision.analyze_scene(image_path)

        response = "📸 **Scene Analyse**\n\n"

        if result.get('thinking'):
            response += f"🤔 **Redenering:**\n{result['thinking']}\n\n"

        response += f"💡 **Analyse:**\n{result['answer']}"

        return response

    def cmd_vision_track(self, image_path: str, target: str) -> str:
        """Track object met vision"""
        result = self.vision.track_object(image_path, target)

        response = f"🎯 **Tracking: {target}**\n\n"
        response += f"📍 **Locatie:**\n{result.get('answer', 'Niet gevonden')}"

        return response

    def cmd_vision_landing(self, image_path: str) -> str:
        """Vind landing zone"""
        result = self.vision.find_landing_zone(image_path)

        response = "🛬 **Landing Zone Detection**\n\n"
        response += f"🎯 **Aanbevolen zone:**\n{result.get('answer', 'Geen veilige zone gevonden')}"

        return response

    def cmd_auto_flight(self, target_x: float, target_y: float,
                       target_z: float = 10.0,
                       camera_view: str = None) -> str:
        """Autonome vlucht met vision"""
        target = Position(target_x, target_y, target_z)

        result = f"🤖 **Autonome Vlucht**\n\nDoel: ({target_x}, {target_y}, {target_z})\n\n"

        if self.vision.autonomous_flight_to(target, camera_view):
            result += "✅ Autonome vlucht succesvol!"
        else:
            result += "❌ Autonome vlucht gefaald!"

        return result

    def cmd_help(self) -> str:
        """Help text voor drone commands"""
        return """
🚁 **Drone Simulator Commands**

**BASIC CONTROL:**
/drone_status - Drone status
/drone_arm - Arm drone (klaar maken)
/drone_takeoff [altitude] - Opstijgen
/drone_land - Landen
/drone_disarm - Disarm (na landing)

**NAVIGATION:**
/drone_goto <x> <y> [z] - Vlieg naar positie
/drone_waypoint <x> <y> [z] - Voeg waypoint toe
/drone_mission - Voer missie uit (alle waypoints)
/drone_clear - Wis waypoints

**VISION CONTROL:**
/drone_vision - Analyseer camera view (stuur foto)
/drone_track <object> - Track object (stuur foto)
/drone_landing - Vind landing zone (stuur foto)
/drone_auto <x> <y> [z] - Autonome vlucht

**EMERGENCY:**
/drone_emergency - NOODLANDING

**INFO:**
/drone_render - Toon wereld (top-down view)
/drone_help - Dit helpbericht

**VOORBEELDEN:**
• /drone_goto 50 50 15
• /drone_waypoint 30 30 10
• /drone_track rode auto (met foto)

⚠️ Dit is een SIMULATOR - veilig testen!
        """.strip()

    def get_quick_stats(self) -> Dict:
        """Quick stats voor dashboard"""
        status = self.drone.get_status()
        vision_status = self.vision.get_vision_status()

        return {
            'state': status['state'],
            'altitude': status['altitude'],
            'battery': status['battery'],
            'waypoints': len(self.drone.waypoints),
            'tracking': vision_status['tracking_target']
        }


# Singleton
_drone_interface: 'DroneInterface' = None

def get_drone_interface() -> DroneInterface:
    """Krijg drone interface (singleton)"""
    global _drone_interface
    if _drone_interface is None:
        _drone_interface = DroneInterface()
    return _drone_interface


# Test
if __name__ == "__main__":
    print("🎮 Drone Interface Test\n")

    interface = get_drone_interface()

    # Test commands
    print(interface.cmd_help())
    print("\n" + "="*50 + "\n")

    print(interface.cmd_arm())
    print(interface.cmd_takeoff(15))
    print("\n" + interface.cmd_status())

    print("\n" + interface.cmd_goto(70, 70))
    print("\n" + interface.cmd_land())

    print("\n✅ Interface test compleet!")
