"""
PersonalAI X-Ray Module
Röntgenfoto analyse module (ALLEEN VOOR EDUCATIE EN ONDERZOEK)
"""

import sys
from pathlib import Path
from typing import Dict, Optional
import logging

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.brain import get_brain

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class XRayAnalyzer:
    """
    Röntgenfoto analyse assistent

    ⚠️ BELANGRIJK: Alleen voor educatieve doeleinden!
    Dit is GEEN medische diagnose tool.
    """

    def __init__(self):
        if not config.ENABLE_XRAY_MODULE:
            raise RuntimeError("X-ray module is uitgeschakeld in config")

        self.brain = get_brain()
        self.disclaimer = config.MEDICAL_DISCLAIMER
        logger.info("🔬 XRayAnalyzer geïnitialiseerd")

    def _add_disclaimer(self, result: Dict) -> Dict:
        """Voeg medische disclaimer toe aan resultaat"""
        result['disclaimer'] = self.disclaimer
        result['is_medical_advice'] = False
        return result

    def analyze_xray(self, image_path: str, focus_area: str = None,
                    thinking: bool = True) -> Dict:
        """
        Algemene röntgen analyse

        Args:
            image_path: Pad naar röntgenfoto
            focus_area: Specifiek gebied om op te focussen (optioneel)
            thinking: Toon redenering

        Returns:
            Dict met analyse EN disclaimer
        """
        if focus_area:
            prompt = f"""
            Analyseer deze röntgenfoto, met speciale aandacht voor: {focus_area}

            Beschrijf:
            1. Wat voor type röntgenfoto is dit? (deel van lichaam, perspectief)
            2. Wat zijn de belangrijkste structuren die zichtbaar zijn?
            3. Zijn er opvallende kenmerken in het {focus_area} gebied?
            4. Algemene observaties over de afbeelding

            DISCLAIMER: Dit is een educatieve analyse, geen medische diagnose.
            """
        else:
            prompt = """
            Analyseer deze röntgenfoto.

            Beschrijf:
            1. Wat voor type röntgenfoto is dit? (deel van lichaam, perspectief)
            2. Wat zijn de belangrijkste anatomische structuren die zichtbaar zijn?
            3. Zijn er opvallende kenmerken of bijzonderheden?
            4. Beeldkwaliteit en positionering

            DISCLAIMER: Dit is een educatieve analyse, geen medische diagnose.
            """

        result = self.brain.analyze(
            image=image_path,
            prompt=prompt,
            task="general",
            thinking=thinking
        )

        return self._add_disclaimer(result)

    def identify_structures(self, image_path: str, structure_name: str,
                          visualize: bool = True) -> Dict:
        """
        Identificeer specifieke anatomische structuren

        Args:
            image_path: Pad naar röntgenfoto
            structure_name: Naam van structuur (bijv. "femur", "ribben")
            visualize: Markeer de structuur

        Returns:
            Dict met locatie van structuur EN disclaimer
        """
        prompt = f"""
        Identificeer de {structure_name} in deze röntgenfoto.
        Geef de locatie aan met een bounding box.

        Dit is voor educatieve doeleinden.
        """

        result = self.brain.find_objects(image_path, prompt, plot=visualize)
        return self._add_disclaimer(result)

    def point_to_anatomy(self, image_path: str, description: str,
                        visualize: bool = True) -> Dict:
        """
        Wijs specifieke anatomische punten aan

        Args:
            image_path: Pad naar röntgenfoto
            description: Beschrijving van punt (bijv. "het midden van de wervel")
            visualize: Teken punten

        Returns:
            Dict met coördinaten EN disclaimer
        """
        prompt = f"""
        Wijs aan: {description}

        Geef exacte punten aan waar dit zich bevindt in de röntgenfoto.
        Dit is voor educatieve analyse.
        """

        result = self.brain.point_to(image_path, prompt, plot=visualize)
        return self._add_disclaimer(result)

    def compare_xrays(self, image_paths: list, question: str = None) -> Dict:
        """
        Vergelijk meerdere röntgenfoto's

        Args:
            image_paths: Lijst met röntgenfoto paden
            question: Vergelijkingsvraag (optioneel)

        Returns:
            Dict met vergelijking EN disclaimer
        """
        if question is None:
            question = """
            Vergelijk deze röntgenfoto's.

            Analyseer:
            1. Wat zijn de overeenkomsten?
            2. Wat zijn de verschillen?
            3. Zijn er progressieve veranderingen zichtbaar?
            4. Algemene observaties

            DISCLAIMER: Dit is educatieve vergelijking, geen medische beoordeling.
            """

        result = self.brain.compare_images(image_paths, question)
        return self._add_disclaimer(result)

    def educational_analysis(self, image_path: str, learning_focus: str) -> Dict:
        """
        Educatieve analyse voor leren

        Args:
            image_path: Pad naar röntgenfoto
            learning_focus: Wat wil je leren? (bijv. "normale anatomie", "beeldvorming technieken")

        Returns:
            Dict met educatieve informatie EN disclaimer
        """
        prompt = f"""
        Gebruik deze röntgenfoto als educatief voorbeeld voor: {learning_focus}

        Leg uit:
        1. Wat kunnen we leren van deze afbeelding?
        2. Welke anatomische structuren zijn goed zichtbaar?
        3. Wat zijn interessante observaties voor leren?
        4. Hoe is de beeldkwaliteit en wat zegt dat over de techniek?

        Benadering: educatief en instructief, niet diagnostisch.
        """

        result = self.brain.deep_analyze(image_path, prompt)
        return self._add_disclaimer(result)

    def quality_assessment(self, image_path: str) -> Dict:
        """
        Beoordeel beeldkwaliteit van röntgenfoto

        Args:
            image_path: Pad naar röntgenfoto

        Returns:
            Dict met kwaliteitsbeoordeling EN disclaimer
        """
        prompt = """
        Beoordeel de kwaliteit van deze röntgenfoto.

        Analyseer:
        1. Is de positionering correct?
        2. Is de belichting adequaat?
        3. Is er bewegingsonscherpte?
        4. Zijn alle relevante structuren zichtbaar?
        5. Algemene technische kwaliteit

        Dit is een technische beoordeling voor educatie.
        """

        result = self.brain.deep_analyze(image_path, prompt)
        return self._add_disclaimer(result)

    def describe_anatomy(self, image_path: str) -> Dict:
        """
        Beschrijf zichtbare anatomie in detail

        Args:
            image_path: Pad naar röntgenfoto

        Returns:
            Dict met anatomische beschrijving EN disclaimer
        """
        prompt = """
        Beschrijf alle zichtbare anatomische structuren in deze röntgenfoto.

        Geef gedetailleerde informatie over:
        1. Botstructuren
        2. Zachte weefsels (indien zichtbaar)
        3. Ruimtes en holtes
        4. Positionering en oriëntatie
        5. Opvallende kenmerken

        Educatief doel: anatomie leren herkennen op röntgenfoto's.
        """

        result = self.brain.deep_analyze(image_path, prompt)
        return self._add_disclaimer(result)

    def get_disclaimer(self) -> str:
        """Krijg de medische disclaimer"""
        return self.disclaimer

    def get_help_text(self) -> str:
        """Krijg help tekst voor X-ray functies"""
        return f"""
🔬 PersonalAI X-Ray Module - EDUCATIEF GEBRUIK

{self.disclaimer}

BESCHIKBARE FUNCTIES:

📊 ALGEMENE ANALYSE:
- analyze_xray() - Algemene röntgen analyse
- describe_anatomy() - Beschrijf anatomie
- educational_analysis() - Educatieve focus

🎯 STRUCTUUR IDENTIFICATIE:
- identify_structures() - Vind specifieke anatomie
- point_to_anatomy() - Wijs anatomische punten aan

📈 VERGELIJKING & KWALITEIT:
- compare_xrays() - Vergelijk meerdere röntgenfoto's
- quality_assessment() - Beoordeel beeldkwaliteit

⚠️ GEBRUIK:
- Alleen voor educatie en onderzoek
- NIET voor medische diagnoses
- NIET voor behandelbeslissingen
- Raadpleeg altijd een arts voor medische zaken

Voor details: help(XRayAnalyzer)
        """


# Singleton instance
_xray_analyzer: Optional[XRayAnalyzer] = None

def get_xray_analyzer() -> XRayAnalyzer:
    """Krijg of maak X-ray analyzer (singleton)"""
    global _xray_analyzer
    if _xray_analyzer is None:
        _xray_analyzer = XRayAnalyzer()
    return _xray_analyzer


# Test code
if __name__ == "__main__":
    print("🔬 XRayAnalyzer Test")
    try:
        analyzer = get_xray_analyzer()
        print(analyzer.get_help_text())
        print("\n✅ X-ray module gereed!")
    except RuntimeError as e:
        print(f"❌ {e}")
        print("💡 Activeer X-ray module in config.py")
