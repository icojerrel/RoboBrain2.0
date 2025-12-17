"""
PersonalAI Configuration
Configuratie voor jouw persoonlijke AI assistent
"""

import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
MEMORY_DIR = DATA_DIR / "memory"

# Maak directories aan
for dir_path in [DATA_DIR, CACHE_DIR, MEMORY_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)

# RoboBrain Model Settings
ROBOBRAIN_MODEL = "BAAI/RoboBrain2.0-7B"  # 7B voor beste balans
ROBOBRAIN_DEVICE = "auto"  # Auto-detect GPU/CPU
DEFAULT_THINKING = True  # Standaard thinking mode aan
DEFAULT_TEMPERATURE = 0.7

# Telegram Bot Settings
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ALLOWED_USERS = os.getenv("TELEGRAM_ALLOWED_USERS", "").split(",")  # Lege lijst = iedereen

# Web Dashboard Settings
WEB_HOST = "127.0.0.1"
WEB_PORT = 7860
WEB_SHARE = False  # Set True voor publieke Gradio link

# Memory Settings
MEMORY_TYPE = "local"  # "local" of "vector" (met ChromaDB)
MAX_CONVERSATION_HISTORY = 50  # Aantal berichten om te onthouden
ENABLE_LONG_TERM_MEMORY = True

# Language Settings
LANGUAGE = "nl"  # Nederlandse interface
DATE_FORMAT = "%d-%m-%Y %H:%M"

# Vision Task Settings
VISION_TASKS = {
    "general": "Algemene visuele analyse",
    "pointing": "Objecten aanwijzen en lokaliseren",
    "affordance": "Grijpbare delen identificeren",
    "trajectory": "Bewegingstraject voorspellen",
    "grounding": "Visueel objecten vinden met bounding boxes"
}

# Module Settings
ENABLE_XRAY_MODULE = True  # Röntgenfoto analyse module
ENABLE_WEB_SEARCH = True  # Web search capabilities
ENABLE_DOCUMENT_ANALYSIS = True  # PDF/document verwerking

# Safety & Privacy
MEDICAL_DISCLAIMER = """
⚠️ MEDISCHE DISCLAIMER:
Deze analyse is alleen voor educatieve en informatieve doeleinden.
Dit is GEEN medisch advies. Raadpleeg altijd een gekwalificeerde arts
voor medische diagnoses en behandeling.
"""

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = DATA_DIR / "personalai.log"

# Performance
MAX_IMAGE_SIZE = (1920, 1080)  # Max resolutie voor snelheid
BATCH_PROCESSING = False  # Voor toekomstige batch analyse

# API Keys (optioneel voor extra features)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

print("✅ PersonalAI configuratie geladen")
print(f"📁 Data directory: {DATA_DIR}")
print(f"🤖 RoboBrain model: {ROBOBRAIN_MODEL}")
print(f"🧠 Thinking mode: {'Aan' if DEFAULT_THINKING else 'Uit'}")
print(f"🔬 X-ray module: {'Actief' if ENABLE_XRAY_MODULE else 'Inactief'}")
