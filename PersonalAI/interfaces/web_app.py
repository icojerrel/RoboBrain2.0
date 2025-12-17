"""
PersonalAI Web Dashboard
Gradio web interface voor PersonalAI
"""

import sys
from pathlib import Path
import logging

try:
    import gradio as gr
except ImportError:
    print("❌ Gradio niet geïnstalleerd!")
    print("📦 Installeer met: pip install gradio")
    sys.exit(1)

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.brain import get_brain
from modules.vision import get_vision_assistant
from modules.xray import get_xray_analyzer if config.ENABLE_XRAY_MODULE else None

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class PersonalAIWebApp:
    """Web interface voor PersonalAI"""

    def __init__(self):
        self.brain = get_brain()
        self.vision = get_vision_assistant()

        self.xray = None
        if config.ENABLE_XRAY_MODULE:
            try:
                self.xray = get_xray_analyzer()
            except:
                logger.warning("X-ray module niet beschikbaar")

        logger.info("🌐 Web app geïnitialiseerd")

    def analyze_image(self, image, question, task_type, thinking):
        """Analyseer afbeelding via web interface"""
        if image is None:
            return "❌ Upload een afbeelding!"

        try:
            # Sla tijdelijk op
            temp_path = config.CACHE_DIR / "web_upload.jpg"
            image.save(temp_path)

            # Analyseer
            result = self.brain.analyze(
                image=str(temp_path),
                prompt=question,
                task=task_type,
                thinking=thinking,
                plot=True
            )

            # Maak response
            response = f"💡 **Antwoord:**\n{result['answer']}\n\n"

            if thinking and result.get('thinking'):
                response += f"🤔 **Redenering:**\n{result['thinking']}\n\n"

            response += f"🎯 **Task:** {task_type}"

            # Lees geannoteerde afbeelding als die bestaat
            result_path = config.BASE_DIR / "result"
            annotated_images = list(result_path.glob("web_upload_with_*"))
            annotated_image = annotated_images[0] if annotated_images else None

            return response, annotated_image

        except Exception as e:
            return f"❌ Fout: {str(e)}", None

    def analyze_xray(self, image, question, thinking):
        """Analyseer röntgenfoto"""
        if not self.xray:
            return "❌ X-ray module niet actief!"

        if image is None:
            return "❌ Upload een röntgenfoto!"

        try:
            temp_path = config.CACHE_DIR / "xray_upload.jpg"
            image.save(temp_path)

            result = self.xray.analyze_xray(
                str(temp_path),
                focus_area=question if question else None,
                thinking=thinking
            )

            response = f"{result.get('disclaimer', '')}\n\n"
            response += f"💡 **Analyse:**\n{result['answer']}\n\n"

            if thinking and result.get('thinking'):
                response += f"🤔 **Redenering:**\n{result['thinking']}"

            return response

        except Exception as e:
            return f"❌ Fout: {str(e)}"

    def create_interface(self):
        """Maak Gradio interface"""

        with gr.Blocks(title="PersonalAI", theme=gr.themes.Soft()) as demo:
            gr.Markdown("""
            # 🤖 PersonalAI - Jouw Persoonlijke AI Assistent
            Powered by RoboBrain 2.0
            """)

            with gr.Tabs():
                # Tab 1: Algemene Vision
                with gr.Tab("📸 Vision Analyse"):
                    gr.Markdown("Upload een afbeelding en stel een vraag")

                    with gr.Row():
                        with gr.Column():
                            vision_image = gr.Image(type="pil", label="Upload Afbeelding")
                            vision_question = gr.Textbox(
                                label="Vraag",
                                placeholder="Wat zie je op deze afbeelding?",
                                value="Beschrijf deze afbeelding in detail."
                            )
                            vision_task = gr.Dropdown(
                                choices=list(config.VISION_TASKS.keys()),
                                value="general",
                                label="Task Type"
                            )
                            vision_thinking = gr.Checkbox(
                                label="Thinking Mode (toon redenering)",
                                value=config.DEFAULT_THINKING
                            )
                            vision_btn = gr.Button("🔍 Analyseer", variant="primary")

                        with gr.Column():
                            vision_output = gr.Textbox(
                                label="Resultaat",
                                lines=15,
                                max_lines=20
                            )
                            vision_annotated = gr.Image(label="Geannoteerde Afbeelding")

                    vision_btn.click(
                        self.analyze_image,
                        inputs=[vision_image, vision_question, vision_task, vision_thinking],
                        outputs=[vision_output, vision_annotated]
                    )

                    # Voorbeelden
                    gr.Examples(
                        examples=[
                            ["Wat is de hoofdkleur?", "general"],
                            ["Vind de persoon met een rode hoed", "grounding"],
                            ["Pak de kop", "affordance"],
                        ],
                        inputs=[vision_question, vision_task]
                    )

                # Tab 2: X-ray (indien actief)
                if self.xray:
                    with gr.Tab("🔬 X-ray Analyse (Educatief)"):
                        gr.Markdown(f"""
                        {config.MEDICAL_DISCLAIMER}

                        Upload een röntgenfoto voor educatieve analyse.
                        """)

                        with gr.Row():
                            with gr.Column():
                                xray_image = gr.Image(type="pil", label="Upload Röntgenfoto")
                                xray_question = gr.Textbox(
                                    label="Focus Gebied (optioneel)",
                                    placeholder="bijv. 'thorax', 'femur'"
                                )
                                xray_thinking = gr.Checkbox(
                                    label="Gedetailleerde Analyse",
                                    value=True
                                )
                                xray_btn = gr.Button("🔬 Analyseer", variant="primary")

                            with gr.Column():
                                xray_output = gr.Textbox(
                                    label="Analyse",
                                    lines=20,
                                    max_lines=25
                                )

                        xray_btn.click(
                            self.analyze_xray,
                            inputs=[xray_image, xray_question, xray_thinking],
                            outputs=xray_output
                        )

                # Tab 3: System Info
                with gr.Tab("ℹ️ Systeem Info"):
                    capabilities = self.brain.get_capabilities()

                    gr.Markdown(f"""
                    ## 🤖 PersonalAI Systeem

                    **Model:** {capabilities['model']}

                    **Thinking Support:** {'✅ Ja' if capabilities['thinking_support'] else '❌ Nee'}

                    **Beschikbare Tasks:**
                    {chr(10).join([f"- {task}: {desc}" for task, desc in config.VISION_TASKS.items()])}

                    **X-ray Module:** {'✅ Actief' if self.xray else '❌ Inactief'}

                    **Taal:** {config.LANGUAGE}

                    **Status:** {'🟢 Operationeel' if capabilities['ready'] else '🔴 Niet Gereed'}

                    ---

                    ### 📝 Over PersonalAI
                    PersonalAI is jouw persoonlijke AI assistent gebouwd op RoboBrain 2.0.
                    Het combineert geavanceerde vision capabilities met een gebruiksvriendelijke interface.

                    **Features:**
                    - Multi-modal visuele analyse
                    - Chain-of-thought reasoning
                    - Robotica planning
                    - Educatieve röntgen analyse
                    - Geheugen en voorkeuren

                    **Telegram Bot ook beschikbaar!**
                    Zie README.md voor instructies.
                    """)

            gr.Markdown("""
            ---
            💡 **Tips:**
            - Upload heldere, goed belichte foto's voor beste resultaten
            - Stel specifieke vragen voor gerichte antwoorden
            - Gebruik thinking mode voor gedetailleerde redenering
            - Voor robotica taken (affordance, trajectory), upload foto's met duidelijke objecten
            """)

        return demo

    def launch(self, share=False):
        """Start de web app"""
        demo = self.create_interface()
        demo.launch(
            server_name=config.WEB_HOST,
            server_port=config.WEB_PORT,
            share=share or config.WEB_SHARE
        )


def main():
    """Main entry point"""
    print("🌐 Starting PersonalAI Web Interface...")

    app = PersonalAIWebApp()
    app.launch()


if __name__ == "__main__":
    main()
