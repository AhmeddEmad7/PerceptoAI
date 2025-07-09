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


class Settings(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)


class ConversationDatabase:
    def __init__(self, db_path: str = "sqlite:///data/databases/conversations.db"):
        self.engine = create_engine(db_path, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        with self.Session() as session:
            if not session.query(Settings).filter_by(key="current_voice").first():
                default_setting = Settings(key="current_voice", value="Sarah")
                session.add(default_setting)
            # Initialize total_interactions_count if it doesn't exist
            if not session.query(Settings).filter_by(key="total_interactions_count").first():
                default_interaction_count = Settings(key="total_interactions_count", value="0")
                session.add(default_interaction_count)
            session.commit()

    def create_new_conversation(self) -> int:
        """Create a new conversation and return its ID."""
        with self.Session() as session:
            conversation = Conversation()
            session.add(conversation)
            session.commit()
            return conversation.id

    def save_message(
        self, user_input: str, ai_response: str, conversation_id: Optional[int] = None
    ) -> int:
        """Save a message to a conversation and return the message ID."""
        with self.Session() as session:
            # If conversation_id is None, it means we need to create a new conversation for this message.
            # This scenario should primarily be handled by the /conversations POST endpoint,
            # but this provides a fallback for the first message if not explicitly created.
            if conversation_id is None:
                conversation_id = self.create_new_conversation()

            message = Message(
                conversation_id=conversation_id,
                user_input=user_input,
                ai_response=ai_response,
            )
            session.add(message)
            session.commit()

            # Increment the total_interactions_count
            total_interactions_setting = session.query(Settings).filter_by(key="total_interactions_count").first()
            if total_interactions_setting:
                total_interactions_setting.value = str(int(total_interactions_setting.value) + 1)
                session.commit()

            return message.id # Return message.id

    def get_messages_from_conversation(
        self, conversation_id: int, limit: int = 100
    ) -> List[Dict]:
        """Retrieve messages from a specific conversation, ordered by timestamp."""
        with self.Session() as session:
            messages = (
                session.query(Message)
                .filter_by(conversation_id=conversation_id)
                .order_by(Message.timestamp.asc()) # Change to ascending order
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
        """Get the total number of interactions (user input + AI response)."""
        with self.Session() as session:
            setting = session.query(Settings).filter_by(key="total_interactions_count").first()
            return int(setting.value) if setting else 0

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

    def get_conversation_details(self, conversation_id: int) -> Optional[Dict]:
        """Retrieve details for a specific conversation by ID, including its title."""
        with self.Session() as session:
            conversation = session.query(Conversation).get(conversation_id)
            if conversation:
                return {
                    "id": conversation.id,
                    "title": conversation.title,
                    "created_at": conversation.created_at.isoformat(),
                }
            return None
        
    def reset_total_interactions_count(self) -> None:
        """Reset the total interactions count to 0."""
        with self.Session() as session:
            setting = session.query(Settings).filter_by(key="total_interactions_count").first()
            if setting:
                setting.value = "0"
                session.commit()
            else:
                # This case should ideally not happen if __init__ sets it up
                new_setting = Settings(key="total_interactions_count", value="0")
                session.add(new_setting)
                session.commit()

    def get_current_voice(self) -> str:
        """Retrieve the current voice from the settings table."""
        with self.Session() as session:
            setting = session.query(Settings).filter_by(key="current_voice").first()
            return setting.value if setting else "Sarah"

    def update_current_voice(self, voice: str) -> None:
        """Update the current voice in the settings table."""
        with self.Session() as session:
            setting = session.query(Settings).filter_by(key="current_voice").first()
            if setting:
                setting.value = voice
            else:
                setting = Settings(key="current_voice", value=voice)
                session.add(setting)
            session.commit()
