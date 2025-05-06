import sqlite3
from typing import List, Dict, Optional

class ConversationDatabase:
    def __init__(self, db_path: str = "databases/conversations.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_input TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create table for conversation count
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_count (
                    id INTEGER PRIMARY KEY,
                    count INTEGER NOT NULL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Initialize count if it doesn't exist
            cursor.execute('''
                INSERT OR IGNORE INTO conversation_count (id, count)
                VALUES (1, 0)
            ''')
            conn.commit()

    def save_conversation(self, user_input: str, ai_response: str, conversation_count_threshold: int) -> (int, int):
        """Save a conversation to the database and return the conversation ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (user_input, ai_response)
                VALUES (?, ?)
            ''', (user_input, ai_response))
            conn.commit()

            self.increment_conversation_count()
            processed_conversations_count = self.get_conversation_count()
            
            if(processed_conversations_count >= conversation_count_threshold):
                self.reset_conversation_count()

            return cursor.lastrowid, processed_conversations_count

    def get_conversations(self, limit: int = 100) -> List[Dict]:
        """Get the last N conversations."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, user_input, ai_response, timestamp
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            return [{
                "id": row[0],
                "user_input": row[1],
                "ai_response": row[2],
                "timestamp": row[3]
            } for row in rows]

    def get_conversation_count(self) -> int:
        """Get the current conversation count."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT count FROM conversation_count WHERE id = 1
            ''')
            result = cursor.fetchone()
            return result[0] if result else 0

    def increment_conversation_count(self):
        """Increment the conversation count and return the new value."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE conversation_count 
                SET count = count + 1, 
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = 1
            ''')
            conn.commit()
    
    def reset_conversation_count(self):
        """Reset the conversation count."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE conversation_count 
                SET count = 0, 
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = 1
            ''')
            conn.commit()

    def get_conversation_by_id(self, conversation_id: int) -> Optional[Dict]:
        """Get a specific conversation by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, user_input, ai_response, timestamp
                FROM conversations
                WHERE id = ?
            ''', (conversation_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "user_input": row[1],
                    "ai_response": row[2],
                    "timestamp": row[3]
                }
            return None
