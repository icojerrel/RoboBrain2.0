"""
PersonalAI Autonomous Memory System

Short-term memory (SQLite) voor recente context
Long-term memory (Qdrant) voor semantic search en learnings
"""

import sqlite3
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Literal
from datetime import datetime
from dataclasses import dataclass, asdict
import logging

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant not available - install: pip install qdrant-client")

import sys
sys.path.append(str(Path(__file__).parent.parent))
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


@dataclass
class ShortTermMemory:
    """Short-term memory entry"""
    id: Optional[int]
    timestamp: str
    type: Literal["action", "observation", "thought", "goal", "result"]
    content: str
    metadata: Optional[Dict] = None


@dataclass
class LongTermMemory:
    """Long-term memory entry"""
    id: str
    timestamp: str
    type: Literal["fact", "skill", "preference", "lesson", "discovery", "pattern"]
    tags: List[str]
    content: str
    importance: int  # 1-10
    metadata: Optional[Dict] = None


class ShortTermMemoryStore:
    """
    SQLite-based short-term memory

    Maintains last 50 entries for immediate context
    Auto-deletes older entries
    """

    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = config.DATA_DIR / "memory" / "short_term.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT
            )
        """)

        # Index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON memories(timestamp DESC)
        """)

        conn.commit()
        conn.close()

    def add(self, type: str, content: str, metadata: Dict = None):
        """Add memory entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute("""
            INSERT INTO memories (timestamp, type, content, metadata)
            VALUES (?, ?, ?, ?)
        """, (timestamp, type, content, metadata_json))

        conn.commit()

        # Keep only last 50 entries
        cursor.execute("""
            DELETE FROM memories
            WHERE id NOT IN (
                SELECT id FROM memories
                ORDER BY timestamp DESC
                LIMIT 50
            )
        """)

        conn.commit()
        conn.close()

        logger.debug(f"📝 Short-term memory: [{type}] {content[:50]}...")

    def get_recent(self, limit: int = 50) -> List[ShortTermMemory]:
        """Get recent memories"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM memories
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            ShortTermMemory(
                id=row['id'],
                timestamp=row['timestamp'],
                type=row['type'],
                content=row['content'],
                metadata=json.loads(row['metadata']) if row['metadata'] else None
            )
            for row in rows
        ]

    def get_by_type(self, type: str, limit: int = 10) -> List[ShortTermMemory]:
        """Get memories of specific type"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM memories
            WHERE type = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (type, limit))

        rows = cursor.fetchall()
        conn.close()

        return [
            ShortTermMemory(
                id=row['id'],
                timestamp=row['timestamp'],
                type=row['type'],
                content=row['content'],
                metadata=json.loads(row['metadata']) if row['metadata'] else None
            )
            for row in rows
        ]

    def clear(self):
        """Clear all memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories")
        conn.commit()
        conn.close()

        logger.info("🗑️ Short-term memory cleared")

    def get_context(self) -> str:
        """Get formatted context from recent memories"""
        memories = self.get_recent(20)

        if not memories:
            return "No recent context available."

        context = "## Recent Context\n\n"

        for mem in reversed(memories):  # Chronological order
            dt = datetime.fromisoformat(mem.timestamp)
            time_str = dt.strftime("%H:%M:%S")
            context += f"**[{time_str}] {mem.type.upper()}:** {mem.content}\n"

        return context


class LongTermMemoryStore:
    """
    Qdrant-based long-term memory with vector embeddings

    Semantic search for relevant past learnings
    Stores only significant discoveries/lessons
    """

    def __init__(self, collection_name: str = "personalai_memory"):
        if not QDRANT_AVAILABLE:
            logger.warning("Qdrant not available - long-term memory disabled")
            self.enabled = False
            return

        self.collection_name = collection_name
        self.client = QdrantClient(host="localhost", port=6333)
        self.enabled = True

        # Check if Qdrant is running
        try:
            self.client.get_collections()
            self._init_collection()
        except Exception as e:
            logger.warning(f"Qdrant not running: {e}")
            self.enabled = False

    def _init_collection(self):
        """Initialize Qdrant collection"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            # Create collection with 1536 dimensions (OpenAI embeddings)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            logger.info(f"✅ Created Qdrant collection: {self.collection_name}")

    def add(self,
            type: str,
            content: str,
            tags: List[str],
            importance: int,
            metadata: Dict = None,
            embedding: List[float] = None):
        """
        Add long-term memory

        Args:
            type: fact|skill|preference|lesson|discovery|pattern
            content: Memory content
            tags: List of tags for categorization
            importance: 1-10 (only store if >= 5)
            metadata: Additional metadata
            embedding: Pre-computed embedding (or will use mock)
        """
        if not self.enabled:
            return

        if importance < 5:
            logger.debug(f"Skipping low-importance memory (importance={importance})")
            return

        # Generate mock embedding if not provided
        # In production: use OpenAI embeddings or sentence-transformers
        if embedding is None:
            embedding = self._generate_mock_embedding(content)

        point = PointStruct(
            id=self._generate_id(),
            vector=embedding,
            payload={
                "timestamp": datetime.now().isoformat(),
                "type": type,
                "tags": tags,
                "content": content,
                "importance": importance,
                "metadata": metadata or {}
            }
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        logger.info(f"🧠 Long-term memory stored: [{type}] {content[:50]}... (importance={importance})")

    def search(self,
               query: str = None,
               query_embedding: List[float] = None,
               type: str = None,
               tags: List[str] = None,
               limit: int = 5) -> List[LongTermMemory]:
        """
        Semantic search for relevant memories

        Args:
            query: Text query (will be embedded)
            query_embedding: Pre-computed query embedding
            type: Filter by type
            tags: Filter by tags
            limit: Max results
        """
        if not self.enabled:
            return []

        # Generate query embedding
        if query_embedding is None and query:
            query_embedding = self._generate_mock_embedding(query)

        if query_embedding is None:
            logger.warning("No query provided for search")
            return []

        # Build filter
        filter_dict = {}
        if type:
            filter_dict["type"] = type
        if tags:
            filter_dict["tags"] = {"$in": tags}

        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=filter_dict if filter_dict else None,
            limit=limit
        )

        return [
            LongTermMemory(
                id=str(result.id),
                timestamp=result.payload["timestamp"],
                type=result.payload["type"],
                tags=result.payload["tags"],
                content=result.payload["content"],
                importance=result.payload["importance"],
                metadata=result.payload.get("metadata")
            )
            for result in results
        ]

    def _generate_id(self) -> str:
        """Generate unique ID"""
        import uuid
        return str(uuid.uuid4())

    def _generate_mock_embedding(self, text: str) -> List[float]:
        """
        Generate mock embedding for testing

        In production: use OpenAI API or sentence-transformers
        """
        import hashlib

        # Deterministic mock embedding based on text hash
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to 1536 floats (OpenAI embedding size)
        embedding = []
        for i in range(1536):
            byte_idx = i % len(hash_bytes)
            value = (hash_bytes[byte_idx] / 255.0) - 0.5  # -0.5 to 0.5
            embedding.append(value)

        return embedding

    def get_all(self, type: str = None, limit: int = 100) -> List[LongTermMemory]:
        """Get all memories (or filtered by type)"""
        if not self.enabled:
            return []

        # Scroll through collection
        results = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )[0]  # Returns (points, next_page_offset)

        memories = []
        for point in results:
            if type and point.payload.get("type") != type:
                continue

            memories.append(LongTermMemory(
                id=str(point.id),
                timestamp=point.payload["timestamp"],
                type=point.payload["type"],
                tags=point.payload["tags"],
                content=point.payload["content"],
                importance=point.payload["importance"],
                metadata=point.payload.get("metadata")
            ))

        return memories


# Singleton instances
_short_term_memory: Optional[ShortTermMemoryStore] = None
_long_term_memory: Optional[LongTermMemoryStore] = None


def get_short_term_memory() -> ShortTermMemoryStore:
    """Get short-term memory instance (singleton)"""
    global _short_term_memory
    if _short_term_memory is None:
        _short_term_memory = ShortTermMemoryStore()
    return _short_term_memory


def get_long_term_memory() -> LongTermMemoryStore:
    """Get long-term memory instance (singleton)"""
    global _long_term_memory
    if _long_term_memory is None:
        _long_term_memory = LongTermMemoryStore()
    return _long_term_memory


# Convenience functions
def remember_short(type: str, content: str, metadata: Dict = None):
    """Quick add to short-term memory"""
    get_short_term_memory().add(type, content, metadata)


def remember_long(type: str, content: str, tags: List[str], importance: int, metadata: Dict = None):
    """Quick add to long-term memory"""
    get_long_term_memory().add(type, content, tags, importance, metadata)


def recall_recent(limit: int = 20) -> List[ShortTermMemory]:
    """Quick recall recent short-term memories"""
    return get_short_term_memory().get_recent(limit)


def recall_relevant(query: str, limit: int = 5) -> List[LongTermMemory]:
    """Quick semantic search in long-term memory"""
    return get_long_term_memory().search(query=query, limit=limit)


# Test
if __name__ == "__main__":
    print("🧠 PersonalAI Autonomous Memory System\n")

    # Short-term memory test
    print("=" * 50)
    print("SHORT-TERM MEMORY TEST")
    print("=" * 50)

    stm = get_short_term_memory()

    stm.add("goal", "Test memory system")
    stm.add("action", "Initialize short-term memory")
    stm.add("observation", "Memory system working")
    stm.add("thought", "Should test long-term memory next")

    recent = stm.get_recent(5)
    print(f"\n📝 Recent memories ({len(recent)}):")
    for mem in reversed(recent):
        print(f"  [{mem.type}] {mem.content}")

    # Long-term memory test
    print("\n" + "=" * 50)
    print("LONG-TERM MEMORY TEST")
    print("=" * 50)

    ltm = get_long_term_memory()

    if ltm.enabled:
        ltm.add(
            type="discovery",
            content="PersonalAI dashcam can detect license plates with high accuracy",
            tags=["dashcam", "anpr", "capability"],
            importance=8
        )

        ltm.add(
            type="lesson",
            content="Yi dashcam jailbreak is easiest method for RTSP access",
            tags=["dashcam", "hardware", "jailbreak"],
            importance=7
        )

        ltm.add(
            type="skill",
            content="Use RoboBrain 7B model for balance between speed and accuracy",
            tags=["ai", "model", "performance"],
            importance=9
        )

        # Search
        print("\n🔍 Search: 'dashcam'")
        results = ltm.search(query="dashcam", limit=3)
        for mem in results:
            print(f"  [{mem.type}] {mem.content} (importance={mem.importance})")
    else:
        print("⚠️ Qdrant not available - long-term memory disabled")
        print("   Install: pip install qdrant-client")
        print("   Start: docker run -p 6333:6333 qdrant/qdrant")

    print("\n✅ Memory system test complete!")
