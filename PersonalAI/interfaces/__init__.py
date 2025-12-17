"""PersonalAI Interfaces"""

__all__ = []

# Telegram bot (optioneel)
try:
    from .telegram_bot import PersonalAIBot
    __all__.append('PersonalAIBot')
except:
    pass

# Web app (optioneel)
try:
    from .web_app import PersonalAIWebApp
    __all__.append('PersonalAIWebApp')
except:
    pass
