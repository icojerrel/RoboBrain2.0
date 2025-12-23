"""
PersonalAI License Plate Recognition (ANPR)
AI-powered automatic number plate recognition met RoboBrain 2.0
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import re

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.brain import get_brain

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


@dataclass
class LicensePlate:
    """License plate detection result"""
    plate_number: str
    bbox: Optional[List[int]]  # [x1, y1, x2, y2]
    confidence: float
    country: Optional[str] = None
    vehicle_type: Optional[str] = None
    timestamp: datetime = None


class LicensePlateAI:
    """
    AI-powered license plate recognition
    Gebruikt RoboBrain 2.0 voor plate detection en OCR
    """

    def __init__(self):
        self.brain = get_brain()

        # Plate history for tracking
        self.plate_history_file = config.DATA_DIR / "plate_history.json"
        self.plate_history = self._load_history()

        # Whitelist/blacklist
        self.whitelist_file = config.DATA_DIR / "plate_whitelist.json"
        self.blacklist_file = config.DATA_DIR / "plate_blacklist.json"
        self.whitelist = self._load_list(self.whitelist_file)
        self.blacklist = self._load_list(self.blacklist_file)

        logger.info("🚗 License Plate AI geïnitialiseerd")

    def _load_history(self) -> List[Dict]:
        """Laad plate history"""
        if self.plate_history_file.exists():
            with open(self.plate_history_file, 'r') as f:
                return json.load(f)
        return []

    def _save_history(self):
        """Sla plate history op"""
        with open(self.plate_history_file, 'w') as f:
            json.dump(self.plate_history, f, indent=2)

    def _load_list(self, filepath: Path) -> List[str]:
        """Laad whitelist of blacklist"""
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return []

    def _save_list(self, filepath: Path, data: List[str]):
        """Sla list op"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def detect_plates(self, image_path: str) -> List[LicensePlate]:
        """
        Detecteer kentekens in afbeelding

        Args:
            image_path: Pad naar afbeelding

        Returns:
            List van gedetecteerde kentekens
        """
        prompt = """
        Detecteer en lees alle kentekens/nummerplaten in deze afbeelding.

        Voor elk kenteken:
        1. Lees het kenteken nummer (exact, inclusief letters en cijfers)
        2. Geef de locatie (bounding box format: [x1, y1, x2, y2])
        3. Land/type kenteken indien herkenbaar
        4. Type voertuig (auto, motor, vrachtwagen, etc.)

        Wees zeer nauwkeurig met het kenteken nummer.
        Als er geen kenteken zichtbaar is, zeg dat expliciet.
        """

        result = self.brain.analyze(
            image=image_path,
            prompt=prompt,
            task="general",
            thinking=True
        )

        # Parse plates
        plates = self._parse_plates(result, image_path)

        logger.info(f"🚗 {len(plates)} kenteken(s) gedetecteerd")

        # Add to history
        for plate in plates:
            self._add_to_history(plate)

        return plates

    def _parse_plates(self, vision_result: Dict, image_path: str) -> List[LicensePlate]:
        """Parse vision result naar LicensePlate objects"""
        plates = []
        answer = vision_result.get('answer', '')

        # Extract plate numbers (common formats)
        # Netherlands: XX-XX-XX, XX-XXX-X, etc.
        # International: various formats

        # Pattern for various plate formats
        plate_patterns = [
            r'([A-Z0-9]{2}-[A-Z0-9]{2}-[A-Z0-9]{2})',  # NL format
            r'([A-Z]{1,3}[- ]?\d{1,4}[- ]?[A-Z]{1,3})',  # General format
            r'([A-Z0-9]{5,8})',  # Simple alphanumeric
        ]

        for pattern in plate_patterns:
            matches = re.findall(pattern, answer, re.IGNORECASE)
            for match in matches:
                plate = LicensePlate(
                    plate_number=match.upper().strip(),
                    bbox=None,  # TODO: Parse from answer
                    confidence=0.75,
                    timestamp=datetime.now()
                )
                plates.append(plate)

        # Parse bbox if present
        bbox_pattern = r'\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]'
        bboxes = re.findall(bbox_pattern, answer)

        for i, bbox_match in enumerate(bboxes):
            if i < len(plates):
                plates[i].bbox = [int(x) for x in bbox_match]

        return plates

    def read_plate(self, image_path: str) -> Optional[str]:
        """
        Lees kenteken van afbeelding (simpel, één kenteken)

        Args:
            image_path: Pad naar afbeelding

        Returns:
            Kenteken nummer of None
        """
        plates = self.detect_plates(image_path)

        if plates:
            return plates[0].plate_number
        return None

    def verify_plate(self, plate_number: str, image_path: str) -> Dict:
        """
        Verifieer of een specifiek kenteken in de afbeelding staat

        Args:
            plate_number: Kenteken om te zoeken
            image_path: Pad naar afbeelding

        Returns:
            Verification result
        """
        prompt = f"""
        Is het kenteken "{plate_number}" zichtbaar in deze afbeelding?

        Controleer:
        1. Is dit exacte kenteken aanwezig?
        2. Is het duidelijk leesbaar?
        3. Op welk type voertuig?
        4. Waar in de afbeelding?

        Antwoord duidelijk met ja of nee, gevolgd door details.
        """

        result = self.brain.analyze(
            image=image_path,
            prompt=prompt,
            task="general",
            thinking=True
        )

        answer_lower = result.get('answer', '').lower()

        # Check for affirmative
        is_present = any(word in answer_lower for word in ['ja,', 'yes,', 'zichtbaar', 'aanwezig'])

        return {
            'plate_present': is_present,
            'plate_number': plate_number,
            'details': result.get('answer'),
            'thinking': result.get('thinking')
        }

    def analyze_vehicle(self, image_path: str) -> Dict:
        """
        Analyseer voertuig in afbeelding

        Args:
            image_path: Pad naar afbeelding

        Returns:
            Vehicle analysis
        """
        prompt = """
        Analyseer het voertuig in deze afbeelding:

        1. Type voertuig (auto, motor, vrachtwagen, bus, etc.)
        2. Merk en model (indien herkenbaar)
        3. Kleur
        4. Kenteken (lees exact)
        5. Conditie (nieuw, gebruikt, schade?)
        6. Andere opvallende kenmerken

        Wees zo specifiek mogelijk.
        """

        result = self.brain.deep_analyze(image_path, prompt)

        return {
            'analysis': result.get('answer'),
            'thinking': result.get('thinking')
        }

    def track_vehicle_entry_exit(self, plate_number: str,
                                 direction: str = "entry") -> Dict:
        """
        Track voertuig entry/exit

        Args:
            plate_number: Kenteken
            direction: "entry" of "exit"

        Returns:
            Tracking info
        """
        event = {
            'plate_number': plate_number,
            'direction': direction,
            'timestamp': datetime.now().isoformat(),
            'status': self._get_plate_status(plate_number)
        }

        self.plate_history.append(event)
        self._save_history()

        logger.info(f"🚗 Vehicle {direction}: {plate_number}")

        return event

    def _get_plate_status(self, plate_number: str) -> str:
        """Krijg status van kenteken (whitelist/blacklist/unknown)"""
        if plate_number in self.whitelist:
            return "whitelist"
        elif plate_number in self.blacklist:
            return "blacklist"
        else:
            return "unknown"

    def add_to_whitelist(self, plate_number: str, note: str = "") -> bool:
        """Voeg kenteken toe aan whitelist"""
        if plate_number not in self.whitelist:
            self.whitelist.append(plate_number)
            self._save_list(self.whitelist_file, self.whitelist)
            logger.info(f"✅ Whitelist: {plate_number}")
            return True
        return False

    def add_to_blacklist(self, plate_number: str, reason: str = "") -> bool:
        """Voeg kenteken toe aan blacklist"""
        if plate_number not in self.blacklist:
            self.blacklist.append(plate_number)
            self._save_list(self.blacklist_file, self.blacklist)
            logger.warning(f"⚠️ Blacklist: {plate_number} - {reason}")
            return True
        return False

    def remove_from_whitelist(self, plate_number: str) -> bool:
        """Verwijder van whitelist"""
        if plate_number in self.whitelist:
            self.whitelist.remove(plate_number)
            self._save_list(self.whitelist_file, self.whitelist)
            return True
        return False

    def remove_from_blacklist(self, plate_number: str) -> bool:
        """Verwijder van blacklist"""
        if plate_number in self.blacklist:
            self.blacklist.remove(plate_number)
            self._save_list(self.blacklist_file, self.blacklist)
            return True
        return False

    def _add_to_history(self, plate: LicensePlate):
        """Voeg plate detection toe aan history"""
        entry = {
            'plate_number': plate.plate_number,
            'timestamp': plate.timestamp.isoformat() if plate.timestamp else datetime.now().isoformat(),
            'confidence': plate.confidence,
            'vehicle_type': plate.vehicle_type,
            'status': self._get_plate_status(plate.plate_number)
        }

        self.plate_history.append(entry)

        # Keep only recent history (last 1000)
        if len(self.plate_history) > 1000:
            self.plate_history = self.plate_history[-1000:]

        self._save_history()

    def get_history(self, limit: int = 50) -> List[Dict]:
        """Krijg recente plate history"""
        return self.plate_history[-limit:]

    def search_history(self, plate_number: str) -> List[Dict]:
        """Zoek plate in history"""
        return [
            entry for entry in self.plate_history
            if entry['plate_number'] == plate_number
        ]

    def get_statistics(self) -> Dict:
        """Krijg statistieken"""
        total = len(self.plate_history)

        whitelist_detections = sum(
            1 for e in self.plate_history
            if e.get('status') == 'whitelist'
        )

        blacklist_detections = sum(
            1 for e in self.plate_history
            if e.get('status') == 'blacklist'
        )

        return {
            'total_detections': total,
            'whitelist_count': len(self.whitelist),
            'blacklist_count': len(self.blacklist),
            'whitelist_detections': whitelist_detections,
            'blacklist_detections': blacklist_detections,
            'unknown_detections': total - whitelist_detections - blacklist_detections
        }

    def export_history(self, filepath: str):
        """Exporteer history naar CSV"""
        import csv

        with open(filepath, 'w', newline='') as f:
            if not self.plate_history:
                return

            writer = csv.DictWriter(f, fieldnames=self.plate_history[0].keys())
            writer.writeheader()
            writer.writerows(self.plate_history)

        logger.info(f"💾 History geëxporteerd naar {filepath}")


# Singleton
_license_plate_ai: Optional[LicensePlateAI] = None


def get_license_plate_ai() -> LicensePlateAI:
    """Krijg license plate AI (singleton)"""
    global _license_plate_ai
    if _license_plate_ai is None:
        _license_plate_ai = LicensePlateAI()
    return _license_plate_ai


# Test
if __name__ == "__main__":
    print("🚗 License Plate AI Test\n")

    lp_ai = get_license_plate_ai()

    print("✅ License Plate AI gereed!")

    # Test whitelist/blacklist
    lp_ai.add_to_whitelist("AB-12-CD", "Eigen auto")
    lp_ai.add_to_blacklist("XX-99-XX", "Verdacht voertuig")

    print(f"\n📋 Whitelist: {lp_ai.whitelist}")
    print(f"⚠️ Blacklist: {lp_ai.blacklist}")

    stats = lp_ai.get_statistics()
    print(f"\n📊 Stats: {stats}")

    print("\n💡 Gebruik:")
    print("  lp_ai.detect_plates(image_path)")
    print("  lp_ai.read_plate(image_path)")
    print("  lp_ai.verify_plate('AB-12-CD', image_path)")
    print("  lp_ai.track_vehicle_entry_exit('AB-12-CD', 'entry')")
