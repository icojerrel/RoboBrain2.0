"""
PersonalAI Face Recognition
AI-powered face detection en recognition met RoboBrain 2.0
"""

import sys
import cv2
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.brain import get_brain

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


@dataclass
class Face:
    """Face detection result"""
    bbox: List[int]  # [x1, y1, x2, y2]
    confidence: float
    person_id: Optional[str] = None
    person_name: Optional[str] = None
    attributes: Optional[Dict] = None


class FaceRecognitionAI:
    """
    AI-powered face recognition met RoboBrain 2.0
    Gebruikt vision AI voor face detection en identification
    """

    def __init__(self):
        self.brain = get_brain()

        # Known faces database
        self.known_faces_db = config.DATA_DIR / "known_faces.json"
        self.known_faces = self._load_known_faces()

        logger.info("👤 Face Recognition AI geïnitialiseerd")

    def _load_known_faces(self) -> Dict:
        """Laad database van bekende gezichten"""
        if self.known_faces_db.exists():
            with open(self.known_faces_db, 'r') as f:
                return json.load(f)
        return {}

    def _save_known_faces(self):
        """Sla bekend gezichten database op"""
        with open(self.known_faces_db, 'w') as f:
            json.dump(self.known_faces, f, indent=2)

    def detect_faces(self, image_path: str) -> List[Face]:
        """
        Detecteer gezichten in afbeelding

        Args:
            image_path: Pad naar afbeelding

        Returns:
            List van gedetecteerde gezichten
        """
        prompt = """
        Detecteer alle gezichten in deze afbeelding.

        Voor elk gezicht, geef:
        - Locatie (bounding box)
        - Aantal gezichten
        - Beschrijving (leeftijd, geslacht indien mogelijk)

        Format: [x1, y1, x2, y2] voor elk gezicht
        """

        result = self.brain.analyze(
            image=image_path,
            prompt=prompt,
            task="general",
            thinking=True
        )

        # Parse faces from result
        faces = self._parse_faces(result)

        logger.info(f"👤 {len(faces)} gezicht(en) gedetecteerd")
        return faces

    def _parse_faces(self, vision_result: Dict) -> List[Face]:
        """Parse vision result naar Face objects"""
        # Simpele parsing - kan verbeterd worden
        import re

        faces = []
        answer = vision_result.get('answer', '')

        # Zoek naar bounding box patterns
        bbox_pattern = r'\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]'
        matches = re.findall(bbox_pattern, answer)

        for match in matches:
            bbox = [int(x) for x in match]
            face = Face(
                bbox=bbox,
                confidence=0.8  # Placeholder
            )
            faces.append(face)

        return faces

    def recognize_face(self, image_path: str, face_bbox: List[int] = None) -> Dict:
        """
        Herken persoon in afbeelding

        Args:
            image_path: Pad naar afbeelding
            face_bbox: Optionele bounding box van gezicht

        Returns:
            Recognition result
        """
        # Build prompt met known faces context
        known_names = list(self.known_faces.keys())

        if known_names:
            prompt = f"""
            Analyseer het gezicht/de gezichten in deze afbeelding.

            Bekende personen in database: {', '.join(known_names)}

            Beantwoord:
            1. Wie zie je? (check tegen bekende namen)
            2. Als onbekend, beschrijf de persoon
            3. Hoeveel personen zie je?
            4. Andere details (leeftijd, expressie, etc.)
            """
        else:
            prompt = """
            Analyseer het gezicht/de gezichten in deze afbeelding.

            Beschrijf:
            1. Hoeveel personen zie je?
            2. Beschrijving van elke persoon
            3. Geschatte leeftijd en geslacht
            4. Gezichtsexpressie
            5. Andere opvallende kenmerken
            """

        result = self.brain.deep_analyze(image_path, prompt)

        # Check if any known person is mentioned
        answer_lower = result.get('answer', '').lower()
        recognized_person = None

        for name in known_names:
            if name.lower() in answer_lower:
                recognized_person = name
                break

        return {
            'recognized': recognized_person is not None,
            'person_name': recognized_person,
            'description': result.get('answer'),
            'thinking': result.get('thinking'),
            'confidence': 0.7 if recognized_person else 0.0
        }

    def add_known_person(self, name: str, description: str,
                        reference_image: str = None) -> bool:
        """
        Voeg persoon toe aan bekende gezichten database

        Args:
            name: Naam van persoon
            description: Beschrijving (voor AI herkenning)
            reference_image: Optionele referentie foto

        Returns:
            Success boolean
        """
        if reference_image:
            # Analyseer referentie foto
            result = self.brain.analyze(
                image=reference_image,
                prompt="Beschrijf deze persoon in detail voor herkenning.",
                task="general",
                thinking=False
            )
            description = result.get('answer', description)

        self.known_faces[name] = {
            'description': description,
            'reference_image': reference_image,
            'added_at': str(Path(__file__).stat().st_mtime)
        }

        self._save_known_faces()

        logger.info(f"✅ Persoon toegevoegd: {name}")
        return True

    def remove_known_person(self, name: str) -> bool:
        """Verwijder persoon uit database"""
        if name in self.known_faces:
            del self.known_faces[name]
            self._save_known_faces()
            logger.info(f"🗑️ Persoon verwijderd: {name}")
            return True
        return False

    def list_known_people(self) -> List[str]:
        """Lijst alle bekende personen"""
        return list(self.known_faces.keys())

    def count_faces(self, image_path: str) -> int:
        """
        Tel aantal gezichten in afbeelding

        Args:
            image_path: Pad naar afbeelding

        Returns:
            Aantal gezichten
        """
        result = self.brain.analyze(
            image=image_path,
            prompt="Hoeveel gezichten/personen zie je? Geef alleen het getal.",
            task="general",
            thinking=False
        )

        # Extract number from answer
        import re
        answer = result.get('answer', '0')
        numbers = re.findall(r'\d+', answer)

        if numbers:
            return int(numbers[0])
        return 0

    def analyze_face_attributes(self, image_path: str) -> Dict:
        """
        Analyseer gezichtsattributen

        Args:
            image_path: Pad naar afbeelding

        Returns:
            Dict met attributen (leeftijd, geslacht, expressie, etc.)
        """
        prompt = """
        Analyseer de gezichtskenmerken in detail:

        1. Geschat leeftijd
        2. Geslacht
        3. Gezichtsexpressie (blij, neutraal, verdrietig, etc.)
        4. Emotionele staat
        5. Bril of accessoires?
        6. Haarkleur en -stijl
        7. Andere opvallende kenmerken

        Wees specifiek en beschrijvend.
        """

        result = self.brain.deep_analyze(image_path, prompt)

        return {
            'attributes': result.get('answer'),
            'thinking': result.get('thinking')
        }

    def detect_multiple_faces(self, image_path: str) -> List[Dict]:
        """
        Detecteer en analyseer meerdere gezichten

        Args:
            image_path: Pad naar afbeelding

        Returns:
            List van face analyses
        """
        # First count
        count = self.count_faces(image_path)

        if count == 0:
            return []

        # Analyze all faces
        prompt = f"""
        Er zijn {count} personen in deze afbeelding.

        Voor elke persoon, beschrijf:
        1. Positie (links/rechts/midden)
        2. Uiterlijk en kenmerken
        3. Wat ze doen
        4. Geschatte leeftijd en geslacht

        Nummer elke persoon.
        """

        result = self.brain.deep_analyze(image_path, prompt)

        # Parse individual faces
        faces = []
        answer = result.get('answer', '')

        # Split by person (assumes numbered list)
        import re
        person_blocks = re.split(r'\n\s*\d+\.', answer)

        for i, block in enumerate(person_blocks[1:], 1):  # Skip first split
            faces.append({
                'person_number': i,
                'description': block.strip(),
                'image_path': image_path
            })

        return faces

    def is_same_person(self, image1: str, image2: str) -> Dict:
        """
        Vergelijk of twee afbeeldingen dezelfde persoon tonen

        Args:
            image1: Eerste afbeelding
            image2: Tweede afbeelding

        Returns:
            Dict met vergelijking
        """
        prompt = """
        Vergelijk de persoon/personen in deze twee afbeeldingen.

        Vragen:
        1. Is dit dezelfde persoon?
        2. Wat zijn de overeenkomsten?
        3. Wat zijn de verschillen?
        4. Confidence level (hoog/gemiddeld/laag)

        Wees specifiek over gezichtskenmerken.
        """

        result = self.brain.compare_images([image1, image2], prompt)

        answer_lower = result.get('answer', '').lower()

        # Check for affirmative keywords
        is_same = any(word in answer_lower for word in [
            'dezelfde', 'same person', 'ja,', 'yes,', 'identiek'
        ])

        return {
            'is_same_person': is_same,
            'analysis': result.get('answer'),
            'thinking': result.get('thinking')
        }


# Singleton
_face_recognition: Optional[FaceRecognitionAI] = None


def get_face_recognition() -> FaceRecognitionAI:
    """Krijg face recognition (singleton)"""
    global _face_recognition
    if _face_recognition is None:
        _face_recognition = FaceRecognitionAI()
    return _face_recognition


# Test
if __name__ == "__main__":
    print("👤 Face Recognition AI Test\n")

    face_rec = get_face_recognition()

    print("✅ Face Recognition gereed!")
    print(f"📋 Bekende personen: {face_rec.list_known_people()}")

    # Test add person
    face_rec.add_known_person(
        "John Doe",
        "Man met bruin haar en bril"
    )

    print(f"📋 Na toevoegen: {face_rec.list_known_people()}")

    print("\n💡 Gebruik:")
    print("  face_rec.detect_faces(image_path)")
    print("  face_rec.recognize_face(image_path)")
    print("  face_rec.count_faces(image_path)")
