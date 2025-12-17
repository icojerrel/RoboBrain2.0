"""
PersonalAI Memory System
Lange-termijn geheugen en conversatie management
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import sys

sys.path.append(str(Path(__file__).parent.parent))
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Een enkel bericht in de conversatie"""
    timestamp: str
    user_id: str
    role: str  # 'user' of 'assistant'
    content: str
    metadata: Optional[Dict] = None

    def to_dict(self):
        return asdict(self)


class ConversationMemory:
    """
    Beheert conversatie geschiedenis per gebruiker
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.memory_file = config.MEMORY_DIR / f"conversation_{user_id}.json"
        self.messages: List[Message] = []
        self._load_memory()

    def _load_memory(self):
        """Laad opgeslagen conversaties"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.messages = [
                        Message(**msg) for msg in data.get('messages', [])
                    ]
                logger.info(f"📚 {len(self.messages)} berichten geladen voor {self.user_id}")
            except Exception as e:
                logger.error(f"Fout bij laden geheugen: {e}")
                self.messages = []
        else:
            logger.info(f"🆕 Nieuwe conversatie voor {self.user_id}")

    def _save_memory(self):
        """Sla conversatie op"""
        try:
            data = {
                'user_id': self.user_id,
                'last_updated': datetime.now().strftime(config.DATE_FORMAT),
                'messages': [msg.to_dict() for msg in self.messages]
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fout bij opslaan geheugen: {e}")

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Voeg bericht toe aan geheugen

        Args:
            role: 'user' of 'assistant'
            content: Inhoud van het bericht
            metadata: Extra informatie (bijv. afbeelding paden, task type)
        """
        message = Message(
            timestamp=datetime.now().strftime(config.DATE_FORMAT),
            user_id=self.user_id,
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)

        # Beperk geheugen tot max aantal berichten
        if len(self.messages) > config.MAX_CONVERSATION_HISTORY:
            self.messages = self.messages[-config.MAX_CONVERSATION_HISTORY:]

        if config.ENABLE_LONG_TERM_MEMORY:
            self._save_memory()

    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Haal recente berichten op"""
        return self.messages[-count:]

    def get_context(self, max_chars: int = 2000) -> str:
        """
        Krijg conversatie context als tekst

        Args:
            max_chars: Maximum aantal karakters

        Returns:
            String met recente conversatie
        """
        context_parts = []
        total_chars = 0

        for msg in reversed(self.messages):
            msg_text = f"{msg.role.upper()}: {msg.content}\n"
            if total_chars + len(msg_text) > max_chars:
                break
            context_parts.insert(0, msg_text)
            total_chars += len(msg_text)

        return "".join(context_parts)

    def search_memory(self, query: str, limit: int = 5) -> List[Message]:
        """
        Zoek in geheugen

        Args:
            query: Zoekterm
            limit: Max aantal resultaten

        Returns:
            List van relevante berichten
        """
        query_lower = query.lower()
        results = [
            msg for msg in self.messages
            if query_lower in msg.content.lower()
        ]
        return results[-limit:]

    def clear_memory(self):
        """Wis alle geheugen"""
        self.messages = []
        if self.memory_file.exists():
            self.memory_file.unlink()
        logger.info(f"🗑️ Geheugen gewist voor {self.user_id}")

    def get_stats(self) -> Dict:
        """Krijg statistieken over geheugen"""
        return {
            'total_messages': len(self.messages),
            'user_messages': sum(1 for m in self.messages if m.role == 'user'),
            'assistant_messages': sum(1 for m in self.messages if m.role == 'assistant'),
            'memory_file': str(self.memory_file),
            'oldest_message': self.messages[0].timestamp if self.messages else None,
            'newest_message': self.messages[-1].timestamp if self.messages else None
        }


class UserPreferences:
    """
    Opslaan van gebruikersvoorkeuren
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.prefs_file = config.MEMORY_DIR / f"preferences_{user_id}.json"
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> Dict:
        """Laad voorkeuren"""
        if self.prefs_file.exists():
            try:
                with open(self.prefs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Fout bij laden voorkeuren: {e}")
        return {
            'thinking_mode': config.DEFAULT_THINKING,
            'language': config.LANGUAGE,
            'default_temperature': config.DEFAULT_TEMPERATURE,
            'enable_xray': config.ENABLE_XRAY_MODULE,
            'custom_settings': {}
        }

    def _save_preferences(self):
        """Sla voorkeuren op"""
        try:
            with open(self.prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fout bij opslaan voorkeuren: {e}")

    def set(self, key: str, value):
        """Zet een voorkeur"""
        self.preferences[key] = value
        self._save_preferences()
        logger.info(f"⚙️ Voorkeur '{key}' ingesteld op '{value}' voor {self.user_id}")

    def get(self, key: str, default=None):
        """Haal een voorkeur op"""
        return self.preferences.get(key, default)

    def get_all(self) -> Dict:
        """Krijg alle voorkeuren"""
        return self.preferences.copy()


# Memory manager voor meerdere gebruikers
_memory_instances: Dict[str, ConversationMemory] = {}
_pref_instances: Dict[str, UserPreferences] = {}


def get_memory(user_id: str) -> ConversationMemory:
    """Krijg of maak geheugen voor gebruiker"""
    if user_id not in _memory_instances:
        _memory_instances[user_id] = ConversationMemory(user_id)
    return _memory_instances[user_id]


def get_preferences(user_id: str) -> UserPreferences:
    """Krijg of maak voorkeuren voor gebruiker"""
    if user_id not in _pref_instances:
        _pref_instances[user_id] = UserPreferences(user_id)
    return _pref_instances[user_id]


# Test code
if __name__ == "__main__":
    print("🧠 Memory System Test")

    # Test conversatie geheugen
    memory = get_memory("test_user")
    memory.add_message("user", "Hallo AI!")
    memory.add_message("assistant", "Hallo! Hoe kan ik je helpen?")

    print(f"\nStats: {memory.get_stats()}")
    print(f"\nContext:\n{memory.get_context()}")

    # Test voorkeuren
    prefs = get_preferences("test_user")
    prefs.set("favorite_color", "blauw")
    print(f"\nVoorkeuren: {prefs.get_all()}")

    print("\n✅ Memory systeem werkt!")
