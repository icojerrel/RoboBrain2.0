"""
PersonalAI Vision Module
Visuele analyse taken met gebruiksvriendelijke interface
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.brain import get_brain

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class VisionAssistant:
    """
    Gebruiksvriendelijke interface voor alle visuele taken
    """

    def __init__(self):
        self.brain = get_brain()
        logger.info("👁️ VisionAssistant geïnitialiseerd")

    def analyze_photo(self, image_path: str, question: str = None,
                     thinking: bool = True) -> Dict:
        """
        Analyseer een foto met optionele vraag

        Args:
            image_path: Pad naar foto
            question: Specifieke vraag (optioneel)
            thinking: Toon redenering

        Returns:
            Dict met analyse
        """
        if question is None:
            question = "Beschrijf wat je in deze afbeelding ziet. Wees gedetailleerd."

        return self.brain.analyze(
            image=image_path,
            prompt=question,
            task="general",
            thinking=thinking
        )

    def what_is_this(self, image_path: str) -> str:
        """
        Snelle identificatie: wat is dit?

        Args:
            image_path: Pad naar foto

        Returns:
            String met beschrijving
        """
        result = self.brain.quick_analyze(
            image_path,
            "Wat is dit? Geef een korte, duidelijke beschrijving."
        )
        return result

    def find_in_image(self, image_path: str, object_name: str,
                      visualize: bool = True) -> Dict:
        """
        Vind een object in de afbeelding

        Args:
            image_path: Pad naar foto
            object_name: Wat te zoeken (bijv. "de rode mok")
            visualize: Teken bounding box

        Returns:
            Dict met locatie en coördinaten
        """
        return self.brain.find_objects(image_path, object_name, plot=visualize)

    def point_to_location(self, image_path: str, description: str,
                         visualize: bool = True) -> Dict:
        """
        Wijs specifieke locaties aan

        Args:
            image_path: Pad naar foto
            description: Waar naar wijzen
            visualize: Teken punten

        Returns:
            Dict met punt coördinaten
        """
        return self.brain.point_to(image_path, description, plot=visualize)

    def where_to_grab(self, image_path: str, action: str,
                      visualize: bool = True) -> Dict:
        """
        Vind waar een robot kan grijpen

        Args:
            image_path: Pad naar foto
            action: Wat te doen (bijv. "til de kop op")
            visualize: Teken grijpgebied

        Returns:
            Dict met affordance gebied
        """
        return self.brain.get_affordance(image_path, action, plot=visualize)

    def plan_movement(self, image_path: str, goal: str,
                     visualize: bool = True) -> Dict:
        """
        Plan bewegingstraject

        Args:
            image_path: Pad naar foto
            goal: Bewegingsdoel
            visualize: Teken traject

        Returns:
            Dict met trajectory punten
        """
        return self.brain.predict_trajectory(image_path, goal, plot=visualize)

    def compare_photos(self, image_paths: List[str], question: str = None) -> Dict:
        """
        Vergelijk meerdere foto's

        Args:
            image_paths: Lijst met foto paden
            question: Vergelijkingsvraag

        Returns:
            Dict met vergelijking
        """
        if question is None:
            question = "Vergelijk deze afbeeldingen. Wat zijn de overeenkomsten en verschillen?"

        return self.brain.compare_images(image_paths, question)

    def describe_in_detail(self, image_path: str) -> Dict:
        """
        Gedetailleerde beschrijving met redenering

        Args:
            image_path: Pad naar foto

        Returns:
            Dict met gedetailleerde analyse en reasoning
        """
        prompt = """
        Geef een zeer gedetailleerde beschrijving van deze afbeelding.
        Include:
        - Wat zijn de hoofdobjecten?
        - Wat is de context/setting?
        - Wat gebeurt er (indien van toepassing)?
        - Interessante details die opvallen
        - Kleuren, texturen, sfeer
        """
        return self.brain.deep_analyze(image_path, prompt)

    def count_objects(self, image_path: str, object_type: str) -> Dict:
        """
        Tel objecten in afbeelding

        Args:
            image_path: Pad naar foto
            object_type: Wat te tellen (bijv. "mensen", "stoelen")

        Returns:
            Dict met aantal en details
        """
        prompt = f"Hoeveel {object_type} zie je in deze afbeelding? Tel ze nauwkeurig en geef details."
        return self.brain.deep_analyze(image_path, prompt)

    def read_text(self, image_path: str) -> str:
        """
        Lees tekst van afbeelding (OCR-achtig)

        Args:
            image_path: Pad naar foto met tekst

        Returns:
            String met gelezen tekst
        """
        return self.brain.quick_analyze(
            image_path,
            "Lees alle tekst die zichtbaar is in deze afbeelding en geef deze weer."
        )

    def analyze_scene(self, image_path: str) -> Dict:
        """
        Analyseer de volledige scène

        Args:
            image_path: Pad naar foto

        Returns:
            Dict met scene analyse
        """
        prompt = """
        Analyseer deze scène volledig:
        1. Waar is dit? (locatie type)
        2. Wat zijn de objecten en hun posities?
        3. Wat is de ruimtelijke layout?
        4. Zijn er mensen? Wat doen ze?
        5. Wat is de algemene sfeer/context?
        """
        return self.brain.deep_analyze(image_path, prompt)

    def safety_check(self, image_path: str) -> Dict:
        """
        Veiligheidscheck van ruimte/situatie

        Args:
            image_path: Pad naar foto

        Returns:
            Dict met veiligheidsanalyse
        """
        prompt = """
        Voer een veiligheidsanalyse uit van deze afbeelding:
        - Zijn er gevaren zichtbaar?
        - Is de omgeving veilig?
        - Obstakels of risico's?
        - Aanbevelingen?
        """
        return self.brain.deep_analyze(image_path, prompt)

    def get_help_text(self) -> str:
        """Krijg help tekst voor alle functies"""
        return """
📸 PersonalAI Vision Module - Beschikbare Functies:

🔍 ALGEMENE ANALYSE:
- analyze_photo() - Algemene foto analyse met vraag
- what_is_this() - Snelle identificatie
- describe_in_detail() - Gedetailleerde beschrijving
- analyze_scene() - Volledige scène analyse

🎯 OBJECT DETECTIE:
- find_in_image() - Vind object met bounding box
- point_to_location() - Wijs specifieke punten aan
- count_objects() - Tel objecten

🤖 ROBOTICA:
- where_to_grab() - Vind grijpgebieden
- plan_movement() - Plan bewegingstraject

📊 VERGELIJKING:
- compare_photos() - Vergelijk meerdere foto's

📝 TEKST & VEILIGHEID:
- read_text() - Lees tekst van afbeelding
- safety_check() - Veiligheidsanalyse

Voor details: help(VisionAssistant)
        """


# Singleton instance
_vision_assistant: Optional[VisionAssistant] = None

def get_vision_assistant() -> VisionAssistant:
    """Krijg of maak vision assistant (singleton)"""
    global _vision_assistant
    if _vision_assistant is None:
        _vision_assistant = VisionAssistant()
    return _vision_assistant


# Test code
if __name__ == "__main__":
    print("👁️ VisionAssistant Test")
    assistant = get_vision_assistant()
    print(assistant.get_help_text())
    print("\n✅ Vision module gereed!")
