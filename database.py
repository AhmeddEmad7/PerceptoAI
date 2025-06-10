from sqlalchemy import (
    ForeignKey,
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import List, Dict, Optional
from datetime import datetime

Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_input = Column(String, nullable=False)
    ai_response = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("Conversation", back_populates="messages")


class ConversationDatabase:
    def __init__(self, db_path: str = "sqlite:///data/databases/conversations.db"):
        self.engine = create_engine(db_path, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def start_new_conversation(self) -> int:
        """Start a new conversation and return its ID."""
        with self.Session() as session:
            conversation = Conversation()
            session.add(conversation)
            session.commit()
            return conversation.id

    def save_message(
        self, user_input: str, ai_response: str, conversation_id: Optional[int] = None
    ) -> int:
        """Save a message to a conversation and return the conversation ID."""
        with self.Session() as session:
            if conversation_id is None:
                conversation_id = self.start_new_conversation()

            message = Message(
                conversation_id=conversation_id,
                user_input=user_input,
                ai_response=ai_response,
            )
            session.add(message)
            session.commit()

            return conversation_id

    def get_messages_from_conversation(
        self, conversation_id: int, limit: int = 100
    ) -> List[Dict]:
        """Retrieve messages from a specific conversation, ordered by timestamp."""
        with self.Session() as session:
            messages = (
                session.query(Message)
                .filter_by(conversation_id=conversation_id)
                .order_by(Message.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "conversation_id": msg.conversation_id,
                    "message_id": msg.id,
                    "user_input": msg.user_input,
                    "ai_response": msg.ai_response,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in messages
            ]

    def get_message_by_id(
        self, conversation_id: int, message_id: int
    ) -> Optional[Dict]:
        """Retrieve a specific message by its ID and conversation ID."""
        with self.Session() as session:
            message = (
                session.query(Message)
                .filter_by(id=message_id, conversation_id=conversation_id)
                .first()
            )
            if message:
                return {
                    "conversation_id": message.conversation_id,
                    "message_id": message.id,
                    "user_input": message.user_input,
                    "ai_response": message.ai_response,
                    "timestamp": message.timestamp.isoformat(),
                }
            return None

    def get_conversation_count(self) -> int:
        """Get the total number of conversations."""
        with self.Session() as session:
            return session.query(func.count(Conversation.id)).scalar()

    def get_latest_conversation_id(self) -> Optional[int]:
        """Get the ID of the latest conversation."""
        with self.Session() as session:
            latest_conversation = (
                session.query(Conversation)
                .order_by(Conversation.created_at.desc())
                .first()
            )
            return latest_conversation.id if latest_conversation else None

    def update_conversation_title(self, conversation_id: int, title: str) -> bool:
        """Update the title of a conversation."""
        with self.Session() as session:
            conversation = session.query(Conversation).get(conversation_id)
            if conversation:
                conversation.title = title
                session.commit()
                return True
            return False

    def get_conversations(self) -> List[Dict]:
        """Retrieve all conversations with their IDs and titles."""
        with self.Session() as session:
            conversations = session.query(Conversation).all()
            return [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                }
                for conv in conversations
            ]
