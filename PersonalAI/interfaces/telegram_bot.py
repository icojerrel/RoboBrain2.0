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
