"""
PersonalAI Telegram Bot
Jouw persoonlijke AI assistent via Telegram
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional
import asyncio

# Telegram imports
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, MessageHandler,
        CallbackQueryHandler, ContextTypes, filters
    )
except ImportError:
    print("❌ python-telegram-bot niet geïnstalleerd!")
    print("📦 Installeer met: pip install python-telegram-bot")
    sys.exit(1)

sys.path.append(str(Path(__file__).parent.parent))
import config
from core.brain import get_brain
from core.memory import get_memory, get_preferences
from modules.vision import get_vision_assistant
from modules.xray import get_xray_analyzer
from modules.drone_interface import get_drone_interface
from modules.dashcam_ai import get_dashcam, RecordingMode, EventType

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=config.LOG_LEVEL
)
logger = logging.getLogger(__name__)


class PersonalAIBot:
    """
    Telegram Bot voor PersonalAI
    """

    def __init__(self, token: str):
        self.token = token
        self.brain = get_brain()
        self.vision = get_vision_assistant()

        # X-ray analyzer (optioneel)
        self.xray = None
        if config.ENABLE_XRAY_MODULE:
            try:
                self.xray = get_xray_analyzer()
            except:
                logger.warning("X-ray module niet beschikbaar")

        # Drone interface
        try:
            self.drone = get_drone_interface()
        except Exception as e:
            logger.warning(f"Drone interface niet beschikbaar: {e}")
            self.drone = None

        # Dashcam
        try:
            self.dashcam = get_dashcam(front_camera="0")
        except Exception as e:
            logger.warning(f"Dashcam niet beschikbaar: {e}")
            self.dashcam = None

        # Autonomous Trader
        try:
            from trading.autonomous_trader import AutonomousTrader
            self.trader = AutonomousTrader(mode="paper")  # Start in safe paper mode
            self.trader_thread = None  # Will hold trader thread when running
        except Exception as e:
            logger.warning(f"Autonomous Trader niet beschikbaar: {e}")
            self.trader = None
            self.trader_thread = None

        self.app = Application.builder().token(token).build()
        self._setup_handlers()

        logger.info("🤖 PersonalAI Telegram Bot geïnitialiseerd")

    def _setup_handlers(self):
        """Configureer alle command en message handlers"""

        # Commands
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("info", self.cmd_info))
        self.app.add_handler(CommandHandler("stats", self.cmd_stats))
        self.app.add_handler(CommandHandler("clear", self.cmd_clear))
        self.app.add_handler(CommandHandler("settings", self.cmd_settings))

        # Vision commands
        self.app.add_handler(CommandHandler("analyze", self.cmd_analyze))
        self.app.add_handler(CommandHandler("find", self.cmd_find))
        self.app.add_handler(CommandHandler("point", self.cmd_point))
        self.app.add_handler(CommandHandler("grab", self.cmd_grab))
        self.app.add_handler(CommandHandler("move", self.cmd_move))
        self.app.add_handler(CommandHandler("compare", self.cmd_compare))

        # X-ray commands (indien ingeschakeld)
        if self.xray:
            self.app.add_handler(CommandHandler("xray", self.cmd_xray))
            self.app.add_handler(CommandHandler("anatomy", self.cmd_anatomy))

        # Drone commands (indien beschikbaar)
        if self.drone:
            self.app.add_handler(CommandHandler("drone_help", self.cmd_drone_help))
            self.app.add_handler(CommandHandler("drone_status", self.cmd_drone_status))
            self.app.add_handler(CommandHandler("drone_arm", self.cmd_drone_arm))
            self.app.add_handler(CommandHandler("drone_disarm", self.cmd_drone_disarm))
            self.app.add_handler(CommandHandler("drone_takeoff", self.cmd_drone_takeoff))
            self.app.add_handler(CommandHandler("drone_land", self.cmd_drone_land))
            self.app.add_handler(CommandHandler("drone_goto", self.cmd_drone_goto))
            self.app.add_handler(CommandHandler("drone_waypoint", self.cmd_drone_waypoint))
            self.app.add_handler(CommandHandler("drone_mission", self.cmd_drone_mission))
            self.app.add_handler(CommandHandler("drone_clear", self.cmd_drone_clear))
            self.app.add_handler(CommandHandler("drone_emergency", self.cmd_drone_emergency))
            self.app.add_handler(CommandHandler("drone_render", self.cmd_drone_render))

        # Dashcam commands (indien beschikbaar)
        if self.dashcam:
            self.app.add_handler(CommandHandler("dashcam_help", self.cmd_dashcam_help))
            self.app.add_handler(CommandHandler("dashcam_status", self.cmd_dashcam_status))
            self.app.add_handler(CommandHandler("dashcam_start", self.cmd_dashcam_start))
            self.app.add_handler(CommandHandler("dashcam_stop", self.cmd_dashcam_stop))
            self.app.add_handler(CommandHandler("dashcam_monitor", self.cmd_dashcam_monitor))
            self.app.add_handler(CommandHandler("dashcam_events", self.cmd_dashcam_events))
            self.app.add_handler(CommandHandler("dashcam_incidents", self.cmd_dashcam_incidents))
            self.app.add_handler(CommandHandler("dashcam_plates", self.cmd_dashcam_plates))
            self.app.add_handler(CommandHandler("dashcam_stats", self.cmd_dashcam_stats))
            self.app.add_handler(CommandHandler("dashcam_export", self.cmd_dashcam_export))

        # Trader commands (indien beschikbaar)
        if self.trader:
            self.app.add_handler(CommandHandler("trader_help", self.cmd_trader_help))
            self.app.add_handler(CommandHandler("trader_start", self.cmd_trader_start))
            self.app.add_handler(CommandHandler("trader_stop", self.cmd_trader_stop))
            self.app.add_handler(CommandHandler("trader_status", self.cmd_trader_status))
            self.app.add_handler(CommandHandler("trader_stats", self.cmd_trader_stats))
            self.app.add_handler(CommandHandler("trader_strategies", self.cmd_trader_strategies))
            self.app.add_handler(CommandHandler("trader_market", self.cmd_trader_market))

        # Message handlers
        self.app.add_handler(MessageHandler(
            filters.PHOTO, self.handle_photo
        ))
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handle_text
        ))

        # Callback handlers voor inline keyboards
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user_id = str(update.effective_user.id)
        user_name = update.effective_user.first_name

        welcome_message = f"""
👋 Hallo {user_name}! Welkom bij PersonalAI!

Ik ben jouw persoonlijke AI assistent met geavanceerde vision capabilities.

🧠 Wat kan ik:
• 📸 Foto's analyseren en begrijpen
• 🎯 Objecten vinden en lokaliseren
• 🤖 Robotica planning en affordances
• 🔬 Röntgenfoto's analyseren (educatief)
• 💬 Gesprekken onthouden
• 🧩 Multi-image vergelijking

📝 Start met:
/help - Zie alle commando's
/info - Info over het systeem
/settings - Jouw instellingen

Of stuur gewoon een foto met een vraag!
        """

        # Initialiseer geheugen voor gebruiker
        memory = get_memory(user_id)
        memory.add_message("assistant", welcome_message)

        await update.message.reply_text(welcome_message)

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """
📚 PersonalAI Commando's

🔍 ALGEMENE ANALYSE:
/analyze - Analyseer een foto (stuur foto + /analyze)
/find <object> - Vind object in foto
/point <beschrijving> - Wijs punten aan
/compare - Vergelijk meerdere foto's

🤖 ROBOTICA:
/grab <actie> - Toon grijpgebieden
/move <doel> - Plan bewegingstraject

🔬 RÖNTGEN (EDUCATIEF):
/xray - Analyseer röntgenfoto
/anatomy <structuur> - Identificeer anatomie

🚗 DASHCAM:
/dashcam_help - Dashcam commands
/dashcam_start - Start recording
/dashcam_status - Status & stats

📈 TRADING:
/trader_help - Trading commands
/trader_start - Start autonomous trader
/trader_status - Trader status & P&L

🚁 DRONE:
/drone_help - Drone simulator commands

⚙️ SYSTEEM:
/info - Systeeminformatie
/stats - Jouw statistieken
/settings - Instellingen aanpassen
/clear - Wis geheugen
/help - Dit helpbericht

💡 TIP: Stuur gewoon een foto met een vraag!
De AI begrijpt natuurlijke taal.

Voorbeeld:
[stuur foto] + "Wat zie je hier?"
[stuur foto] + "Vind de rode mok"
        """
        await update.message.reply_text(help_text)

    async def cmd_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Info command"""
        capabilities = self.brain.get_capabilities()

        info_text = f"""
🤖 PersonalAI Systeem Info

📊 Model: {capabilities['model']}
🧠 Thinking Mode: {'✅ Beschikbaar' if capabilities['thinking_support'] else '❌ Niet beschikbaar'}
🎯 Vision Tasks: {len(capabilities['tasks'])}
🔬 X-ray Module: {'✅ Actief' if self.xray else '❌ Inactief'}

💾 Status: {'🟢 Operationeel' if capabilities['ready'] else '🔴 Niet gereed'}

🌐 Versie: PersonalAI v1.0
📅 Taal: Nederlands
        """
        await update.message.reply_text(info_text)

    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stats command"""
        user_id = str(update.effective_user.id)
        memory = get_memory(user_id)
        stats = memory.get_stats()

        stats_text = f"""
📊 Jouw Statistieken

💬 Totaal berichten: {stats['total_messages']}
👤 Jouw berichten: {stats['user_messages']}
🤖 AI berichten: {stats['assistant_messages']}

📅 Eerste bericht: {stats['oldest_message'] or 'Nog geen'}
🕒 Laatste bericht: {stats['newest_message'] or 'Nog geen'}
        """
        await update.message.reply_text(stats_text)

    async def cmd_clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear memory command"""
        user_id = str(update.effective_user.id)
        memory = get_memory(user_id)
        memory.clear_memory()

        await update.message.reply_text("🗑️ Geheugen gewist! Nieuwe start.")

    async def cmd_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Settings command"""
        user_id = str(update.effective_user.id)
        prefs = get_preferences(user_id)
        current_prefs = prefs.get_all()

        keyboard = [
            [InlineKeyboardButton(
                f"Thinking Mode: {'✅' if current_prefs.get('thinking_mode', True) else '❌'}",
                callback_data="toggle_thinking"
            )],
            [InlineKeyboardButton(
                f"X-ray Module: {'✅' if current_prefs.get('enable_xray', False) else '❌'}",
                callback_data="toggle_xray"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        settings_text = f"""
⚙️ Jouw Instellingen

Klik op de knoppen om aan/uit te zetten:

🔧 Huidige instellingen:
• Thinking Mode: {current_prefs.get('thinking_mode', True)}
• Temperatuur: {current_prefs.get('default_temperature', 0.7)}
• Taal: {current_prefs.get('language', 'nl')}
        """

        await update.message.reply_text(
            settings_text,
            reply_markup=reply_markup
        )

    async def cmd_analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze command"""
        await update.message.reply_text(
            "📸 Stuur een foto om te analyseren!\n\n"
            "Je kunt ook een specifieke vraag meesturen:\n"
            "[foto] + /analyze Wat zijn de kleuren?"
        )

    async def cmd_find(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Find object command"""
        if not context.args:
            await update.message.reply_text(
                "🎯 Gebruik: /find <object>\n"
                "Bijvoorbeeld: /find de rode mok\n\n"
                "Stuur eerst een foto, dan dit commando!"
            )
            return

        # Wacht op foto in handle_photo
        context.user_data['pending_command'] = {
            'type': 'find',
            'query': ' '.join(context.args)
        }
        await update.message.reply_text(
            f"🔍 Zoeken naar: {' '.join(context.args)}\n"
            "Stuur nu een foto!"
        )

    async def cmd_xray(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """X-ray analysis command"""
        if not self.xray:
            await update.message.reply_text(
                "❌ X-ray module is niet actief.\n"
                "Activeer in instellingen of config."
            )
            return

        await update.message.reply_text(
            f"{config.MEDICAL_DISCLAIMER}\n\n"
            "🔬 Stuur een röntgenfoto voor educatieve analyse!"
        )

    # Drone commands
    async def cmd_drone_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Drone help command"""
        if not self.drone:
            await update.message.reply_text("❌ Drone module niet beschikbaar")
            return
        await update.message.reply_text(self.drone.cmd_help())

    async def cmd_drone_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Drone status"""
        if not self.drone:
            return
        await update.message.reply_text(self.drone.cmd_status())

    async def cmd_drone_arm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Arm drone"""
        if not self.drone:
            return
        await update.message.reply_text(self.drone.cmd_arm())

    async def cmd_drone_disarm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Disarm drone"""
        if not self.drone:
            return
        await update.message.reply_text(self.drone.cmd_disarm())

    async def cmd_drone_takeoff(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Takeoff command"""
        if not self.drone:
            return
        altitude = float(context.args[0]) if context.args else 15.0
        await update.message.reply_text(self.drone.cmd_takeoff(altitude))

    async def cmd_drone_land(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Land drone"""
        if not self.drone:
            return
        await update.message.reply_text(self.drone.cmd_land())

    async def cmd_drone_goto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Goto position"""
        if not self.drone:
            return
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /drone_goto <x> <y> [z]")
            return
        x = float(context.args[0])
        y = float(context.args[1])
        z = float(context.args[2]) if len(context.args) > 2 else None
        await update.message.reply_text(self.drone.cmd_goto(x, y, z))

    async def cmd_drone_waypoint(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add waypoint"""
        if not self.drone:
            return
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /drone_waypoint <x> <y> [z]")
            return
        x = float(context.args[0])
        y = float(context.args[1])
        z = float(context.args[2]) if len(context.args) > 2 else 15.0
        await update.message.reply_text(self.drone.cmd_waypoint(x, y, z))

    async def cmd_drone_mission(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute mission"""
        if not self.drone:
            return
        await update.message.reply_text(self.drone.cmd_mission())

    async def cmd_drone_clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear waypoints"""
        if not self.drone:
            return
        await update.message.reply_text(self.drone.cmd_clear_waypoints())

    async def cmd_drone_emergency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Emergency stop"""
        if not self.drone:
            return
        await update.message.reply_text(self.drone.cmd_emergency())

    async def cmd_drone_render(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Render world view"""
        if not self.drone:
            return
        output_path = self.drone.cmd_render()
        # Send as photo
        with open(output_path, 'rb') as photo:
            await update.message.reply_photo(photo, caption="🚁 Drone World View")

    # ===== DASHCAM COMMANDS =====

    async def cmd_dashcam_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Dashcam help"""
        if not self.dashcam:
            return
        help_text = """
🚗 PersonalAI Smart Dashcam Commands

**Recording:**
/dashcam_start - Start continuous recording
/dashcam_stop - Stop recording
/dashcam_monitor - Monitoring zonder opname

**Info:**
/dashcam_status - Huidige status
/dashcam_stats - Statistieken
/dashcam_events - Recente events (10)
/dashcam_incidents - Kritieke incidenten
/dashcam_plates - Gedetecteerde kentekens
/dashcam_export - Exporteer events naar CSV

**Features:**
✅ Automatic incident detection
✅ License plate recognition (ANPR)
✅ Traffic sign detection
✅ Lane departure warnings
✅ Driver monitoring (if enabled)
✅ GPS tracking (if enabled)
        """
        await update.message.reply_text(help_text)

    async def cmd_dashcam_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Dashcam status"""
        if not self.dashcam:
            return
        stats = self.dashcam.get_statistics()

        message = f"🚗 Dashcam Status\n\n"
        message += f"Recording: {'✅ Actief' if stats['is_recording'] else '❌ Uit'}\n"
        message += f"Monitoring: {'✅ Actief' if stats['is_monitoring'] else '❌ Uit'}\n"
        message += f"Mode: {stats['recording_mode']}\n"
        message += f"GPS: {'✅ Enabled' if stats['gps_enabled'] else '❌ Disabled'}\n"
        message += f"Driver Monitoring: {'✅ Actief' if stats['driver_monitoring'] else '❌ Uit'}\n\n"
        message += f"📊 Total Events: {stats['total_events']}\n"

        await update.message.reply_text(message)

    async def cmd_dashcam_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start dashcam recording"""
        if not self.dashcam:
            return

        # Parse mode from args
        mode = RecordingMode.CONTINUOUS
        if context.args:
            mode_arg = context.args[0].lower()
            if mode_arg == "event":
                mode = RecordingMode.EVENT_ONLY
            elif mode_arg == "parking":
                mode = RecordingMode.PARKING

        success = self.dashcam.start_recording(mode)

        if success:
            await update.message.reply_text(
                f"✅ Dashcam recording gestart!\n"
                f"Mode: {mode.value}\n\n"
                f"AI monitort nu automatisch je rit.\n"
                f"Events worden automatisch gedetecteerd."
            )
        else:
            await update.message.reply_text("❌ Kon dashcam niet starten")

    async def cmd_dashcam_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop dashcam"""
        if not self.dashcam:
            return

        self.dashcam.stop_recording()
        await update.message.reply_text("⏹️ Dashcam gestopt")

    async def cmd_dashcam_monitor(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start monitoring zonder recording"""
        if not self.dashcam:
            return

        success = self.dashcam.start_monitoring()

        if success:
            await update.message.reply_text(
                "👁️ Monitoring gestart (zonder video opname)\n"
                "Events en snapshots worden wel gelogd."
            )
        else:
            await update.message.reply_text("❌ Kon monitoring niet starten")

    async def cmd_dashcam_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Recente events"""
        if not self.dashcam:
            return

        limit = 10
        if context.args and context.args[0].isdigit():
            limit = int(context.args[0])

        events = self.dashcam.get_events(limit=limit)

        if not events:
            await update.message.reply_text("📊 Geen events gevonden")
            return

        message = f"📊 Recente Events ({len(events)}):\n\n"

        for i, event in enumerate(reversed(events), 1):
            message += f"{i}. **{event.event_type.value}**\n"
            message += f"   ⏰ {event.timestamp.strftime('%H:%M:%S')}\n"
            message += f"   🎯 Severity: {event.severity}\n"
            message += f"   📝 {event.description}\n"

            if event.speed:
                message += f"   🚗 Speed: {event.speed:.1f} km/h\n"

            message += "\n"

        await update.message.reply_text(message)

    async def cmd_dashcam_incidents(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kritieke incidenten"""
        if not self.dashcam:
            return

        critical = self.dashcam.get_events(severity="critical", limit=10)
        high = self.dashcam.get_events(severity="high", limit=10)

        incidents = critical + high

        if not incidents:
            await update.message.reply_text("✅ Geen incidenten")
            return

        message = f"🚨 Incidenten ({len(incidents)}):\n\n"

        for event in incidents[-5:]:  # Last 5
            message += f"**{event.event_type.value}**\n"
            message += f"⏰ {event.timestamp.strftime('%Y-%m-%d %H:%M')}\n"
            message += f"❗ {event.severity.upper()}\n"
            message += f"📝 {event.description}\n"

            if event.video_clip_path:
                message += f"🎥 Clip: {Path(event.video_clip_path).name}\n"

            message += "\n"

            # Send snapshot if available
            if event.snapshot_path and Path(event.snapshot_path).exists():
                with open(event.snapshot_path, 'rb') as photo:
                    await update.message.reply_photo(
                        photo,
                        caption=f"{event.event_type.value} - {event.description}"
                    )

        await update.message.reply_text(message)

    async def cmd_dashcam_plates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gedetecteerde kentekens"""
        if not self.dashcam:
            return

        plate_events = self.dashcam.get_events(
            event_type=EventType.LICENSE_PLATE_DETECTED,
            limit=20
        )

        if not plate_events:
            await update.message.reply_text("🚗 Geen kentekens gedetecteerd")
            return

        message = f"🚗 Kentekens ({len(plate_events)}):\n\n"

        for event in plate_events[-10:]:  # Last 10
            plate = event.metadata.get('plate', 'Unknown')
            message += f"• {plate}\n"
            message += f"  ⏰ {event.timestamp.strftime('%H:%M:%S')}\n"

            if event.location:
                lat = event.location.get('latitude', 0)
                lon = event.location.get('longitude', 0)
                message += f"  📍 {lat:.4f}, {lon:.4f}\n"

            message += "\n"

        await update.message.reply_text(message)

    async def cmd_dashcam_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Dashcam statistieken"""
        if not self.dashcam:
            return

        stats = self.dashcam.get_statistics()

        message = f"📊 Dashcam Statistieken\n\n"
        message += f"**Totaal:** {stats['total_events']} events\n\n"

        message += "**Per Type:**\n"
        for etype, count in stats['events_by_type'].items():
            message += f"  • {etype}: {count}\n"

        message += "\n**Per Severity:**\n"
        for severity, count in stats['events_by_severity'].items():
            message += f"  • {severity}: {count}\n"

        await update.message.reply_text(message)

    async def cmd_dashcam_export(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Exporteer events"""
        if not self.dashcam:
            return

        export_path = config.DATA_DIR / "dashcam" / "events_export.csv"
        self.dashcam.export_events(str(export_path), format="csv")

        # Send file
        with open(export_path, 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename="dashcam_events.csv",
                caption="📊 Dashcam events export"
            )

    # ===== END DASHCAM COMMANDS =====

    # ===== TRADER COMMANDS =====

    async def cmd_trader_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trader help"""
        if not self.trader:
            return
        help_text = """
📈 PersonalAI Autonomous Trader Commands

**Trading:**
/trader_start [paper|live] - Start autonomous trader
/trader_stop - Stop trader
/trader_status - Current status & positions

**Analytics:**
/trader_stats - Performance statistics
/trader_strategies - List strategies & performance
/trader_market - Current market data

**Features:**
✅ MT5 Integration (MNQ futures)
✅ Self-generating strategies
✅ Autonomous backtesting
✅ Risk management (1% per trade, 3% daily max)
✅ Paper trading mode (safe testing)
✅ Self-learning from P&L

⚠️ **RISK WARNING:**
Trading involves substantial risk of loss.
Start with paper mode for testing!
        """
        await update.message.reply_text(help_text)

    async def cmd_trader_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start autonomous trader"""
        if not self.trader:
            return

        # Check if already running
        if self.trader_thread and self.trader_thread.is_alive():
            await update.message.reply_text("⚠️ Trader is al actief!\nGebruik /trader_stop om te stoppen.")
            return

        # Parse mode from args (paper or live)
        mode = "paper"  # Default safe mode
        if context.args:
            mode_arg = context.args[0].lower()
            if mode_arg in ["paper", "live"]:
                mode = mode_arg

        # Warning for live mode
        if mode == "live":
            await update.message.reply_text(
                "⚠️ **LIVE TRADING MODE**\n\n"
                "Dit gebruikt ECHT GELD!\n"
                "Zeker weten? Stuur nogmaals:\n"
                "/trader_start live_confirmed"
            )
            return

        # Recreate trader with selected mode
        from trading.autonomous_trader import AutonomousTrader
        self.trader = AutonomousTrader(mode=mode)

        # Start trader in background thread
        import threading
        self.trader_thread = threading.Thread(target=self.trader.start, daemon=True)
        self.trader_thread.start()

        await update.message.reply_text(
            f"✅ Autonomous Trader gestart!\n\n"
            f"Mode: {mode.upper()}\n"
            f"Symbol: MNQ (Micro E-mini NASDAQ)\n"
            f"Cycle: 5 minutes\n\n"
            f"Decision Loop:\n"
            f"  1. READ - Market data + memory\n"
            f"  2. QUERY - Successful strategies\n"
            f"  3. THINK - Generate/select strategy\n"
            f"  4. ACT - Backtest → Trade\n"
            f"  5. RECORD - Results to memory\n"
            f"  6. LEARN - Improve from P&L\n\n"
            f"Gebruik /trader_status voor live updates."
        )

    async def cmd_trader_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop trader"""
        if not self.trader:
            return

        if not self.trader_thread or not self.trader_thread.is_alive():
            await update.message.reply_text("ℹ️ Trader is niet actief")
            return

        # Stop trader
        self.trader.running = False

        await update.message.reply_text("⏹️ Autonomous Trader gestopt")

    async def cmd_trader_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trader status"""
        if not self.trader:
            return

        # Check if connected to MT5
        if not self.trader.mt5.connect():
            await update.message.reply_text("❌ Niet verbonden met MT5")
            return

        # Get account info
        account = self.trader.mt5.get_account_info()
        positions = self.trader.mt5.get_positions()
        price = self.trader.mt5.get_current_price()

        # Build status message
        message = f"📈 Trader Status\n\n"
        message += f"Mode: {self.trader.mode.upper()}\n"
        message += f"Running: {'✅ Actief' if self.trader.running else '❌ Gestopt'}\n"
        message += f"Cycles: {self.trader.cycle_count}\n\n"

        if account:
            message += f"💰 Account:\n"
            message += f"  Balance: ${account['balance']:.2f}\n"
            message += f"  Equity: ${account['equity']:.2f}\n"
            message += f"  Profit: ${account['profit']:.2f}\n\n"

        if price:
            message += f"📊 MNQ Price:\n"
            message += f"  Bid: ${price['bid']:.2f}\n"
            message += f"  Ask: ${price['ask']:.2f}\n\n"

        message += f"📍 Positions: {len(positions)}\n"

        if positions:
            message += "\nOpen positions:\n"
            for pos in positions:
                message += f"  • {pos.type} {pos.volume} @ ${pos.open_price:.2f}\n"
                message += f"    P&L: ${pos.profit:.2f}\n"

        if self.trader.current_strategy:
            message += f"\n🎯 Active Strategy:\n"
            message += f"  {self.trader.current_strategy.get_name()}\n"

        await update.message.reply_text(message)

    async def cmd_trader_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trading statistics"""
        if not self.trader:
            return

        # Get strategy performance
        strategies = self.trader.strategy_performance

        message = f"📊 Trading Statistics\n\n"
        message += f"Total strategies tested: {len(strategies)}\n\n"

        if strategies:
            message += "**Strategy Performance:**\n"
            # Sort by Sharpe ratio
            sorted_strategies = sorted(
                strategies.items(),
                key=lambda x: x[1].sharpe_ratio,
                reverse=True
            )

            for name, result in sorted_strategies[:5]:  # Top 5
                message += f"\n• {name}\n"
                message += f"  Return: {result.total_return*100:.2f}%\n"
                message += f"  Sharpe: {result.sharpe_ratio:.2f}\n"
                message += f"  Max DD: {result.max_drawdown*100:.2f}%\n"
                message += f"  Win Rate: {result.win_rate*100:.1f}%\n"
                message += f"  Trades: {result.total_trades}\n"
        else:
            message += "No strategies tested yet.\n"
            message += "Trader will generate strategies automatically."

        await update.message.reply_text(message)

    async def cmd_trader_strategies(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List strategies"""
        if not self.trader:
            return

        from pathlib import Path

        strategies_dir = Path(__file__).parent.parent / "trading" / "strategies"

        if not strategies_dir.exists():
            await update.message.reply_text("📁 No strategies directory found")
            return

        strategy_files = list(strategies_dir.glob("*.py"))

        if not strategy_files:
            await update.message.reply_text("📝 No strategies generated yet")
            return

        message = f"📝 Generated Strategies ({len(strategy_files)}):\n\n"

        for filepath in sorted(strategy_files, reverse=True)[:10]:  # Last 10
            name = filepath.stem
            message += f"• {name}\n"

            # Check if we have performance data
            if name in self.trader.strategy_performance:
                result = self.trader.strategy_performance[name]
                message += f"  Sharpe: {result.sharpe_ratio:.2f}\n"
                message += f"  Return: {result.total_return*100:.2f}%\n"

        await update.message.reply_text(message)

    async def cmd_trader_market(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Current market data"""
        if not self.trader:
            return

        # Connect to MT5
        if not self.trader.mt5.connect():
            await update.message.reply_text("❌ Niet verbonden met MT5")
            return

        # Get current price
        price = self.trader.mt5.get_current_price()

        # Get recent bars
        bars = self.trader.mt5.get_bars(count=100)

        if not price or bars is None:
            await update.message.reply_text("❌ Kon market data niet ophalen")
            return

        # Calculate some metrics
        current_close = bars['close'].iloc[-1]
        sma_20 = bars['close'].rolling(20).mean().iloc[-1]
        sma_50 = bars['close'].rolling(50).mean().iloc[-1]
        atr = self.trader.risk_mgr.calculate_atr(bars)

        message = f"📊 MNQ Market Data\n\n"
        message += f"💵 Price:\n"
        message += f"  Bid: ${price['bid']:.2f}\n"
        message += f"  Ask: ${price['ask']:.2f}\n"
        message += f"  Spread: ${price['ask'] - price['bid']:.2f}\n\n"

        message += f"📈 Technical:\n"
        message += f"  Close: ${current_close:.2f}\n"
        message += f"  SMA(20): ${sma_20:.2f}\n"
        message += f"  SMA(50): ${sma_50:.2f}\n"
        message += f"  ATR(14): ${atr:.2f}\n\n"

        # Trend
        if current_close > sma_20 > sma_50:
            message += f"📊 Trend: ⬆️ Uptrend\n"
        elif current_close < sma_20 < sma_50:
            message += f"📊 Trend: ⬇️ Downtrend\n"
        else:
            message += f"📊 Trend: ↔️ Ranging\n"

        await update.message.reply_text(message)

    # ===== END TRADER COMMANDS =====

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle foto uploads"""
        user_id = str(update.effective_user.id)
        memory = get_memory(user_id)
        prefs = get_preferences(user_id)

        # Download foto
        photo_file = await update.message.photo[-1].get_file()
        photo_path = config.CACHE_DIR / f"{user_id}_{update.message.message_id}.jpg"
        await photo_file.download_to_drive(photo_path)

        # Krijg caption als vraag
        caption = update.message.caption or "Beschrijf deze afbeelding in detail."

        # Opslaan in geheugen
        memory.add_message("user", f"[Foto] {caption}", {
            'image_path': str(photo_path)
        })

        await update.message.reply_text("🔄 Analyseren...")

        try:
            # Analyseer met vision assistant
            thinking = prefs.get('thinking_mode', True)
            result = self.vision.analyze_photo(
                str(photo_path),
                caption,
                thinking=thinking
            )

            # Stuur antwoord
            response = f"💡 {result['answer']}"

            if thinking and result.get('thinking'):
                response = f"🤔 Redenering:\n{result['thinking']}\n\n{response}"

            await update.message.reply_text(response)

            # Opslaan antwoord
            memory.add_message("assistant", response)

        except Exception as e:
            error_msg = f"❌ Fout bij analyse: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"Error analyzing photo: {e}")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = str(update.effective_user.id)
        memory = get_memory(user_id)
        text = update.message.text

        memory.add_message("user", text)

        # Eenvoudig antwoord (kan later uitgebreid worden met GPT/Claude)
        response = (
            "💬 Ik heb je bericht ontvangen!\n\n"
            "Momenteel ben ik gespecialiseerd in visuele analyse. "
            "Stuur een foto en ik help je graag!\n\n"
            "Gebruik /help voor alle commando's."
        )

        await update.message.reply_text(response)
        memory.add_message("assistant", response)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()

        user_id = str(query.from_user.id)
        prefs = get_preferences(user_id)

        if query.data == "toggle_thinking":
            current = prefs.get('thinking_mode', True)
            prefs.set('thinking_mode', not current)
            await query.edit_message_text(
                f"✅ Thinking mode: {'AAN' if not current else 'UIT'}\n\n"
                "Gebruik /settings om opnieuw te openen."
            )

        elif query.data == "toggle_xray":
            current = prefs.get('enable_xray', False)
            prefs.set('enable_xray', not current)
            await query.edit_message_text(
                f"✅ X-ray module: {'AAN' if not current else 'UIT'}\n\n"
                "Gebruik /settings om opnieuw te openen."
            )

    def run(self):
        """Start de bot"""
        logger.info("🚀 Starting PersonalAI Telegram Bot...")
        logger.info("🤖 Bot is klaar! Stuur een bericht op Telegram.")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    token = config.TELEGRAM_TOKEN

    if not token:
        print("❌ Geen Telegram bot token gevonden!")
        print("📝 Zet TELEGRAM_BOT_TOKEN in je environment variables")
        print("   of pas config.py aan")
        print("\n💡 Maak een bot met @BotFather op Telegram")
        return

    bot = PersonalAIBot(token)
    bot.run()


if __name__ == "__main__":
    main()
