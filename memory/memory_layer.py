import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

# --- Core Memory (Immutable, JSON) ---
class CoreMemory:
    def __init__(self, path: str):
        self.path = path
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def all(self):
        return self.data

# --- Session Memory (Live, SQLite) ---
class SessionMemory:
    def __init__(self, db_path: str, session_id: Optional[str] = None):
        self.db_path = db_path
        self.session_id = session_id or datetime.utcnow().strftime('%Y-%m-%dT%H-%M')
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS summary_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TEXT,
            text TEXT,
            screen_event TEXT,
            annotation TEXT DEFAULT ''
        )''')
        try:
            c.execute('ALTER TABLE summary_chunks ADD COLUMN annotation TEXT DEFAULT ""')
        except sqlite3.OperationalError:
            pass
        self.conn.commit()

    def add_chunk(self, text: str, screen_event: Optional[str] = None, annotation: str = ""):
        ts = datetime.utcnow().isoformat()
        c = self.conn.cursor()
        c.execute('INSERT INTO summary_chunks (session_id, timestamp, text, screen_event, annotation) VALUES (?, ?, ?, ?, ?)',
                  (self.session_id, ts, text, screen_event, annotation))
        self.conn.commit()

    def get_chunks(self, since: Optional[str] = None) -> List[Dict[str, Any]]:
        c = self.conn.cursor()
        if since:
            c.execute('SELECT timestamp, text, screen_event, annotation FROM summary_chunks WHERE session_id = ? AND timestamp > ? ORDER BY timestamp', (self.session_id, since))
        else:
            c.execute('SELECT timestamp, text, screen_event, annotation FROM summary_chunks WHERE session_id = ? ORDER BY timestamp', (self.session_id,))
        return [
            {'timestamp': row[0], 'text': row[1], 'screen_event': row[2], 'annotation': row[3]}
            for row in c.fetchall()
        ]

    def update_annotation(self, timestamp: str, annotation: str):
        c = self.conn.cursor()
        c.execute('UPDATE summary_chunks SET annotation = ? WHERE session_id = ? AND timestamp = ?',
                  (annotation, self.session_id, timestamp))
        self.conn.commit()

    def summarize(self) -> str:
        # Stub: Replace with LLM summarization
        chunks = self.get_chunks()
        return "\n".join([c['text'] for c in chunks])

    def close(self):
        self.conn.close()

    def update_text(self, timestamp: str, new_text: str):
        c = self.conn.cursor()
        c.execute('UPDATE summary_chunks SET text = ? WHERE session_id = ? AND timestamp = ?',
                  (new_text, self.session_id, timestamp))
        self.conn.commit()

    def delete_chunk(self, timestamp: str):
        c = self.conn.cursor()
        c.execute('DELETE FROM summary_chunks WHERE session_id = ? AND timestamp = ?',
                  (self.session_id, timestamp))
        self.conn.commit()

# --- Long-Term Memory (ChromaDB) ---
class LongTermMemory:
    def __init__(self, persist_dir: str):
        from chromadb import Client as ChromaClient
        from chromadb.config import Settings as ChromaSettings
        self.chroma_client = ChromaClient(ChromaSettings(persist_directory=persist_dir))
        self.collection = self.chroma_client.get_or_create_collection("long_term_memory")
        self.embedder = None  # Lazy load

    def _get_embedder(self):
        if self.embedder is None:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        return self.embedder

    def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        embedder = self._get_embedder()
        embedding = embedder.encode([text])[0]
        meta = metadata or {}
        self.collection.add(documents=[text], embeddings=[embedding], metadatas=[meta], ids=[str(hash(text))])

    def search(self, query: str, top_k: int = 3):
        embedder = self._get_embedder()
        embedding = embedder.encode([query])[0]
        results = self.collection.query(query_embeddings=[embedding], n_results=top_k)
        return results

# --- Memory Layer Orchestrator ---
class MemoryLayer:
    def __init__(self, core_path: str, session_db: str, long_term_dir: str, session_id: Optional[str] = None):
        self.core = CoreMemory(core_path)
        self.session = SessionMemory(session_db, session_id=session_id)
        self.long_term = LongTermMemory(long_term_dir)

    def sync_session_to_long_term(self):
        # Stub: Summarize session and add to long-term memory
        summary = self.session.summarize()
        meta = {"date": datetime.utcnow().date().isoformat()}
        self.long_term.add_memory(summary, metadata=meta)

    def close(self):
        self.session.close()

    def get_memory_stats(self):
        return {
            'session': {'chunks': len(self.session.get_chunks())},
            'long_term': 'N/A',
            'core': list(self.core.all().keys())
        }

    def save_all_memory(self):
        self.session.close()

    def move_chunk_to_core(self, timestamp):
        chunk = next((c for c in self.session.get_chunks() if c['timestamp'] == timestamp), None)
        if chunk:
            self.core.data[chunk['timestamp']] = chunk
            with open(self.core.path, 'w', encoding='utf-8') as f:
                json.dump(self.core.data, f, indent=2)

    def move_chunk_to_long_term(self, timestamp):
        chunk = next((c for c in self.session.get_chunks() if c['timestamp'] == timestamp), None)
        if chunk:
            self.long_term.add_memory(chunk['text'], metadata={'timestamp': chunk['timestamp'], 'annotation': chunk.get('annotation', '')})

    def set_summarization_threshold(self, threshold):
        self.summarization_threshold = threshold

    def summarize_if_needed(self):
        if len(self.session.get_chunks()) >= getattr(self, 'summarization_threshold', 20):
            self.sync_session_to_long_term()
            # Optionally clear session memory after summarization

    def inject_persona_settings(self, prompt, wit_level, verbosity):
        persona = f"Wit: {wit_level}, Verbosity: {verbosity}"
        return f"{persona}\n{prompt}" 