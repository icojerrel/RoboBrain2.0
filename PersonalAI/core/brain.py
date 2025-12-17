"""
PersonalAI Brain - RoboBrain 2.0 Integration
Het visuele brein van jouw persoonlijke assistent
"""

import sys
from pathlib import Path

# Add parent directory to path for RoboBrain import
sys.path.append(str(Path(__file__).parent.parent.parent))

from inference import UnifiedInference
from typing import Union, Dict, List, Optional
import logging

# Import config
sys.path.append(str(Path(__file__).parent.parent))
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class PersonalBrain:
    """
    De AI brain die alle visuele taken afhandelt met RoboBrain 2.0
    """

    def __init__(self, model_id: str = None, device_map: str = None):
        """
        Initialiseer het AI brein

        Args:
            model_id: RoboBrain model (default: 7B uit config)
            device_map: Device mapping (default: auto)
        """
        self.model_id = model_id or config.ROBOBRAIN_MODEL
        self.device_map = device_map or config.ROBOBRAIN_DEVICE

        logger.info(f"🧠 Initialiseren PersonalBrain met {self.model_id}")

        try:
            self.model = UnifiedInference(self.model_id, self.device_map)
            self.is_ready = True
            logger.info("✅ PersonalBrain gereed!")
        except Exception as e:
            logger.error(f"❌ Fout bij laden model: {e}")
            self.is_ready = False
            raise

    def analyze(self,
                image: Union[str, List[str]],
                prompt: str,
                task: str = "general",
                thinking: bool = None,
                plot: bool = False,
                temperature: float = None) -> Dict:
        """
        Analyseer afbeelding(en) met een vraag

        Args:
            image: Pad naar afbeelding of lijst van paden
            prompt: De vraag of instructie
            task: Type taak (general/pointing/affordance/trajectory/grounding)
            thinking: Thinking mode aan/uit (default: config)
            plot: Visualiseer resultaat op afbeelding
            temperature: Sampling temperature

        Returns:
            Dict met 'answer', optioneel 'thinking', en 'task_type'
        """
        if not self.is_ready:
            raise RuntimeError("Brain is niet geïnitialiseerd")

        thinking = thinking if thinking is not None else config.DEFAULT_THINKING
        temperature = temperature or config.DEFAULT_TEMPERATURE

        logger.info(f"🔍 Analyse starten: task={task}, thinking={thinking}")
        logger.info(f"📝 Prompt: {prompt}")

        try:
            result = self.model.inference(
                text=prompt,
                image=image,
                task=task,
                enable_thinking=thinking,
                plot=plot,
                do_sample=True,
                temperature=temperature
            )

            result['task_type'] = task
            logger.info(f"✅ Analyse compleet")

            return result

        except Exception as e:
            logger.error(f"❌ Fout tijdens analyse: {e}")
            return {
                'answer': f"Fout tijdens analyse: {str(e)}",
                'thinking': '',
                'task_type': task,
                'error': str(e)
            }

    def quick_analyze(self, image: Union[str, List[str]], prompt: str) -> str:
        """
        Snelle analyse zonder thinking (alleen antwoord)

        Args:
            image: Afbeelding(en)
            prompt: Vraag

        Returns:
            String met antwoord
        """
        result = self.analyze(image, prompt, thinking=False)
        return result.get('answer', 'Geen antwoord beschikbaar')

    def deep_analyze(self, image: Union[str, List[str]], prompt: str) -> Dict:
        """
        Diepgaande analyse met thinking mode

        Args:
            image: Afbeelding(en)
            prompt: Vraag

        Returns:
            Dict met 'answer' en 'thinking'
        """
        return self.analyze(image, prompt, thinking=True)

    def find_objects(self, image: str, object_description: str, plot: bool = True) -> Dict:
        """
        Vind objecten in afbeelding met bounding boxes

        Args:
            image: Pad naar afbeelding
            object_description: Beschrijving van het object
            plot: Visualiseer bounding boxes

        Returns:
            Dict met resultaat en coördinaten
        """
        return self.analyze(image, object_description, task="grounding", plot=plot)

    def point_to(self, image: str, description: str, plot: bool = True) -> Dict:
        """
        Wijs specifieke punten aan in afbeelding

        Args:
            image: Pad naar afbeelding
            description: Waar naar wijzen
            plot: Visualiseer punten

        Returns:
            Dict met punten als coördinaten
        """
        return self.analyze(image, description, task="pointing", plot=plot)

    def get_affordance(self, image: str, action: str, plot: bool = True) -> Dict:
        """
        Vind waar een robot kan grijpen voor een actie

        Args:
            image: Pad naar afbeelding
            action: De uit te voeren actie (bijv. "pak de kop")
            plot: Visualiseer grijpgebied

        Returns:
            Dict met affordance gebied
        """
        return self.analyze(image, action, task="affordance", plot=plot)

    def predict_trajectory(self, image: str, goal: str, plot: bool = True) -> Dict:
        """
        Voorspel bewegingstraject naar doel

        Args:
            image: Pad naar afbeelding
            goal: Het doel (bijv. "pak de banaan")
            plot: Visualiseer traject

        Returns:
            Dict met trajectory punten
        """
        return self.analyze(image, goal, task="trajectory", plot=plot)

    def compare_images(self, images: List[str], question: str) -> Dict:
        """
        Vergelijk meerdere afbeeldingen

        Args:
            images: Lijst met afbeeldingspaden
            question: Vraag over de afbeeldingen

        Returns:
            Dict met vergelijkend antwoord
        """
        return self.analyze(images, question, task="general", thinking=True)

    def get_capabilities(self) -> Dict:
        """
        Krijg informatie over capabilities van het brein

        Returns:
            Dict met model info en capabilities
        """
        return {
            'model': self.model_id,
            'thinking_support': self.model.supports_thinking,
            'tasks': list(config.VISION_TASKS.keys()),
            'ready': self.is_ready
        }


# Singleton instance voor hergebruik
_brain_instance: Optional[PersonalBrain] = None

def get_brain() -> PersonalBrain:
    """
    Krijg of maak het AI brein (singleton)
    """
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = PersonalBrain()
    return _brain_instance


# Test code
if __name__ == "__main__":
    print("🧠 PersonalBrain Test")
    brain = get_brain()
    print(f"Capabilities: {brain.get_capabilities()}")
    print("✅ Brain is klaar voor gebruik!")
