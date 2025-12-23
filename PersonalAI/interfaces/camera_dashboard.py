"""
PersonalAI Live Camera Dashboard
Web interface met live camera feeds, face recognition en license plate reading
"""

import sys
import cv2
import base64
import threading
from pathlib import Path
from typing import Dict, List, Optional
import logging
import time

try:
    import gradio as gr
except ImportError:
    print("❌ Gradio niet geïnstalleerd!")
    sys.exit(1)

sys.path.append(str(Path(__file__).parent.parent))
import config
from modules.camera_monitor import get_camera_manager
from modules.vision_monitor import get_vision_monitor
from modules.ezviz_integration import get_ezviz_manager

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class CameraDashboard:
    """
    Live camera monitoring dashboard
    Met face recognition, license plate reading en event tracking
    """

    def __init__(self):
        self.camera_manager = get_camera_manager()
        self.vision_monitor = get_vision_monitor()
        self.ezviz_manager = get_ezviz_manager()

        # Live feed state
        self.live_feeds = {}
        self.feed_threads = {}
        self.is_streaming = False

        logger.info("📊 Camera Dashboard geïnitialiseerd")

    def frame_to_base64(self, frame) -> str:
        """Convert frame naar base64 voor web display"""
        if frame is None:
            return None

        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode()
        return f"data:image/jpeg;base64,{jpg_as_text}"

    def get_live_frame(self, camera_name: str):
        """Krijg live frame van camera"""
        camera = self.camera_manager.get_camera(camera_name)
        if camera and camera.is_running:
            return camera.last_frame
        return None

    def setup_ezviz_camera_ui(self, name: str, ip: str, password: str) -> str:
        """Setup EZVIZ camera via UI"""
        try:
            camera = self.ezviz_manager.add_husky_air(name, ip, password)

            if camera:
                camera.start_stream("sub")
                return f"✅ EZVIZ camera '{name}' toegevoegd en gestart!"
            else:
                return "❌ Kon camera niet toevoegen"

        except Exception as e:
            return f"❌ Error: {str(e)}"

    def take_snapshot_ui(self, camera_name: str):
        """Neem snapshot via UI"""
        if not camera_name:
            return None, "❌ Selecteer een camera"

        snapshot_path = self.camera_manager.get_snapshot(camera_name)

        if snapshot_path:
            return snapshot_path, f"✅ Snapshot opgeslagen: {snapshot_path}"
        else:
            return None, "❌ Kon geen snapshot maken"

    def analyze_camera_ui(self, camera_name: str, query: str):
        """Analyseer camera via UI"""
        if not camera_name:
            return "❌ Selecteer een camera"

        if not query:
            query = "Beschrijf wat je ziet in deze camera feed."

        result = self.vision_monitor.analyze_snapshot(camera_name, query)

        response = f"**Analyse van {camera_name}:**\n\n"

        if result.get('thinking'):
            response += f"🤔 **Redenering:**\n{result['thinking']}\n\n"

        response += f"💡 **Antwoord:**\n{result['answer']}"

        return response

    def find_object_ui(self, camera_name: str, object_desc: str):
        """Vind object in camera view"""
        if not camera_name or not object_desc:
            return None, "❌ Camera naam en object beschrijving vereist"

        result = self.vision_monitor.find_object(camera_name, object_desc)

        # Get annotated image
        import glob
        result_images = glob.glob(str(config.BASE_DIR / "result" / "*.jpg"))

        if result_images:
            latest_image = max(result_images, key=lambda x: Path(x).stat().st_mtime)
            return latest_image, f"📍 Locatie: {result.get('answer', 'Niet gevonden')}"
        else:
            return None, f"📍 {result.get('answer', 'Niet gevonden')}"

    def count_people_ui(self, camera_name: str):
        """Tel mensen in camera view"""
        if not camera_name:
            return "❌ Selecteer een camera"

        result = self.vision_monitor.count_people(camera_name)

        response = f"**People Count - {camera_name}:**\n\n"

        if result.get('thinking'):
            response += f"🤔 {result['thinking']}\n\n"

        response += f"👥 {result['answer']}"

        return response

    def get_events_ui(self, limit: int = 10):
        """Krijg recente events voor UI"""
        events = self.vision_monitor.get_events(limit=limit)

        if not events:
            return "📊 Geen events gevonden"

        response = f"**Recente Events ({len(events)}):**\n\n"

        for i, event in enumerate(reversed(events), 1):
            response += f"{i}. **{event.event_type.value}**\n"
            response += f"   📹 Camera: {event.camera_name}\n"
            response += f"   ⏰ Tijd: {event.timestamp.strftime('%H:%M:%S')}\n"
            response += f"   📝 {event.description}\n"
            response += f"   🎯 Confidence: {event.confidence:.0%}\n\n"

        return response

    def start_monitoring_ui(self):
        """Start monitoring via UI"""
        try:
            self.vision_monitor.start_monitoring()
            return "✅ Monitoring gestart! Events worden nu automatisch gedetecteerd."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def stop_monitoring_ui(self):
        """Stop monitoring via UI"""
        self.vision_monitor.stop_monitoring()
        return "⏸️ Monitoring gestopt"

    def get_camera_list(self) -> List[str]:
        """Krijg lijst van camera namen"""
        return list(self.camera_manager.cameras.keys())

    def get_monitoring_status(self) -> str:
        """Krijg monitoring status"""
        status = self.vision_monitor.get_status()

        response = "**Monitoring Status:**\n\n"
        response += f"🔄 Active: {'Ja' if status['is_monitoring'] else 'Nee'}\n"
        response += f"📹 Cameras: {status['cameras_active']}\n"
        response += f"📊 Total Events: {status['total_events']}\n"
        response += f"⏱️ Interval: {status['analysis_interval']}s\n\n"

        response += "**Events per Type:**\n"
        for etype, count in status['event_types'].items():
            if count > 0:
                response += f"  • {etype}: {count}\n"

        return response

    def create_dashboard(self):
        """Maak Gradio dashboard"""

        with gr.Blocks(title="PersonalAI Camera Dashboard", theme=gr.themes.Soft()) as demo:
            gr.Markdown("""
            # 📹 PersonalAI Camera Dashboard
            **Live Monitoring met AI Vision, Face Recognition & License Plate Reading**
            """)

            with gr.Tabs():
                # Tab 1: Camera Setup
                with gr.Tab("⚙️ Camera Setup"):
                    gr.Markdown("### EZVIZ Camera Toevoegen")

                    with gr.Row():
                        setup_name = gr.Textbox(label="Camera Naam", placeholder="Bijv: Woonkamer")
                        setup_ip = gr.Textbox(label="IP Adres", placeholder="192.168.1.100")
                        setup_pass = gr.Textbox(label="Wachtwoord", type="password")

                    setup_btn = gr.Button("➕ Camera Toevoegen", variant="primary")
                    setup_output = gr.Textbox(label="Status", lines=3)

                    setup_btn.click(
                        self.setup_ezviz_camera_ui,
                        inputs=[setup_name, setup_ip, setup_pass],
                        outputs=setup_output
                    )

                    gr.Markdown("### Actieve Cameras")
                    camera_list_display = gr.Textbox(
                        label="Cameras",
                        value=lambda: "\n".join(self.get_camera_list()) or "Geen cameras",
                        lines=5
                    )

                # Tab 2: Live View
                with gr.Tab("📹 Live View"):
                    gr.Markdown("### Live Camera Feed")

                    with gr.Row():
                        live_camera_select = gr.Dropdown(
                            choices=self.get_camera_list,
                            label="Selecteer Camera",
                            interactive=True
                        )
                        refresh_btn = gr.Button("🔄 Refresh Camera List")

                    refresh_btn.click(
                        lambda: gr.Dropdown(choices=self.get_camera_list()),
                        outputs=live_camera_select
                    )

                    live_image = gr.Image(label="Live Feed")

                    with gr.Row():
                        snapshot_btn = gr.Button("📸 Snapshot", variant="primary")

                    snapshot_output = gr.Textbox(label="Snapshot Status")

                    snapshot_btn.click(
                        self.take_snapshot_ui,
                        inputs=live_camera_select,
                        outputs=[live_image, snapshot_output]
                    )

                # Tab 3: AI Analysis
                with gr.Tab("🤖 AI Analysis"):
                    gr.Markdown("### Vision Analysis")

                    analysis_camera = gr.Dropdown(
                        choices=self.get_camera_list,
                        label="Camera"
                    )

                    analysis_query = gr.Textbox(
                        label="Vraag",
                        placeholder="Wat zie je? Hoeveel mensen? etc.",
                        value="Beschrijf wat je ziet"
                    )

                    with gr.Row():
                        analyze_btn = gr.Button("🔍 Analyseer", variant="primary")
                        count_btn = gr.Button("👥 Tel Mensen")

                    analysis_output = gr.Textbox(label="Analyse Resultaat", lines=10)

                    analyze_btn.click(
                        self.analyze_camera_ui,
                        inputs=[analysis_camera, analysis_query],
                        outputs=analysis_output
                    )

                    count_btn.click(
                        self.count_people_ui,
                        inputs=analysis_camera,
                        outputs=analysis_output
                    )

                # Tab 4: Object Finding
                with gr.Tab("🔍 Object Finding"):
                    gr.Markdown("### Vind Objects in Camera View")

                    find_camera = gr.Dropdown(
                        choices=self.get_camera_list,
                        label="Camera"
                    )

                    find_object = gr.Textbox(
                        label="Object Beschrijving",
                        placeholder="Bijv: mijn autosleutels, de rode mok, etc."
                    )

                    find_btn = gr.Button("🎯 Zoek Object", variant="primary")

                    with gr.Row():
                        find_image = gr.Image(label="Gevonden Object (met bounding box)")
                        find_output = gr.Textbox(label="Resultaat", lines=5)

                    find_btn.click(
                        self.find_object_ui,
                        inputs=[find_camera, find_object],
                        outputs=[find_image, find_output]
                    )

                # Tab 5: Face Recognition (Coming soon)
                with gr.Tab("👤 Face Recognition"):
                    gr.Markdown("""
                    ### Face Recognition (In Development)

                    **Features:**
                    - Detect faces in camera feed
                    - Recognize known individuals
                    - Track face locations
                    - Alert on unknown faces

                    🚧 **Status:** Module wordt gebouwd...
                    """)

                # Tab 6: License Plate (Coming soon)
                with gr.Tab("🚗 License Plates"):
                    gr.Markdown("""
                    ### License Plate Recognition (In Development)

                    **Features:**
                    - Automatic license plate detection
                    - OCR for plate numbers
                    - Vehicle tracking
                    - Entry/exit logging

                    🚧 **Status:** Module wordt gebouwd...
                    """)

                # Tab 7: Events & Monitoring
                with gr.Tab("📊 Events & Monitoring"):
                    gr.Markdown("### Monitoring Control")

                    with gr.Row():
                        start_monitor_btn = gr.Button("▶️ Start Monitoring", variant="primary")
                        stop_monitor_btn = gr.Button("⏸️ Stop Monitoring")

                    monitor_status = gr.Textbox(label="Status", lines=2)

                    start_monitor_btn.click(
                        self.start_monitoring_ui,
                        outputs=monitor_status
                    )

                    stop_monitor_btn.click(
                        self.stop_monitoring_ui,
                        outputs=monitor_status
                    )

                    gr.Markdown("### Status Overview")

                    status_display = gr.Textbox(
                        label="Monitoring Status",
                        lines=10,
                        value=self.get_monitoring_status
                    )

                    gr.Markdown("### Recent Events")

                    events_limit = gr.Slider(
                        minimum=5,
                        maximum=50,
                        value=10,
                        step=5,
                        label="Aantal Events"
                    )

                    events_display = gr.Textbox(label="Events", lines=15)

                    refresh_events_btn = gr.Button("🔄 Refresh Events")

                    refresh_events_btn.click(
                        self.get_events_ui,
                        inputs=events_limit,
                        outputs=events_display
                    )

            gr.Markdown("""
            ---
            💡 **Tips:**
            - Start met het toevoegen van je EZVIZ camera in de Setup tab
            - Gebruik Live View om snapshots te maken
            - AI Analysis voor gedetailleerde scene understanding
            - Start Monitoring voor automatische event detection

            **PersonalAI Camera Dashboard v1.0** | Powered by RoboBrain 2.0
            """)

        return demo

    def launch(self, share=False, port=7861):
        """Start dashboard"""
        demo = self.create_dashboard()

        logger.info(f"🚀 Starting Camera Dashboard op port {port}...")

        demo.launch(
            server_name=config.WEB_HOST,
            server_port=port,
            share=share
        )


def main():
    """Main entry point"""
    print("📹 PersonalAI Camera Dashboard")
    print("=" * 50)

    dashboard = CameraDashboard()
    dashboard.launch()


if __name__ == "__main__":
    main()
