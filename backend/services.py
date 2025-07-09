import os
from typing import Optional
from fastapi import HTTPException
import whisper
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from datetime import datetime
import chromadb
from backend.database import ConversationDatabase
import uuid
from textblob import TextBlob
from backend.config.elevenlabs_voice_config import ELEVENLABS_VOICE_IDs, TONE_SETTINGS
from haystack.components.generators.openai import OpenAIGenerator

load_dotenv()


async def convert_audio_to_text(audio_path: str) -> str:
    """
    Convert audio to text using Whisper model
    """
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        
        return result["text"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")


async def convert_text_to_speech(answer: str, prompt: str = None, voice_name: str = "Sarah") -> str:
    """
    Convert text to speech using ElevenLabs with basic tone adjustment based on sentiment.
    """
    try:
        if not os.getenv("ELEVEN_LABS_API_KEY"):
            raise HTTPException(status_code=500, detail="ELEVEN_LABS_API_KEY not found in .env file")

        tone = "neutral"
        if prompt:
            analysis = TextBlob(prompt)
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity

            if polarity > 0.4:
                tone = "happy"
            elif polarity < -0.6:
                tone = "sad"
            elif polarity < -0.3:
                tone = "serious"
            elif subjectivity > 0.6:
                tone = "empathetic"

        voice_id = ELEVENLABS_VOICE_IDs[voice_name]
        client = ElevenLabs(api_key=os.getenv("ELEVEN_LABS_API_KEY"))
        
        audio = client.text_to_speech.convert(
            text=answer,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            voice_settings=TONE_SETTINGS[tone]
        )

        output_path = f"data/model_outputs/output_{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.mp3"
        os.makedirs("data/model_outputs", exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        return output_path

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")


def save_conversation(data: dict, conversation_id: Optional[int] = None) -> dict:
    """
    Save conversation to SQLite and non-question inputs to ChromaDB with embeddings
    """
    try:
        # Saving in SQLite
        conversation_db = ConversationDatabase()
        full_response = (
            data["ai_response"]["answer"]
            + f"\n\nSources Links: {data['ai_response']['url']}"
            if data["ai_response"]["url"] is not None
            else data["ai_response"]["answer"]
        )

        if conversation_id is None:
            latest_conversation_id = conversation_db.get_latest_conversation_id()
            if latest_conversation_id is None:
                # This case should ideally be handled by create_new_conversation endpoint,
                # but as a fallback, we'll let save_message create a new one if needed.
                final_conversation_id = None
            else:
                final_conversation_id = latest_conversation_id
        else:
            final_conversation_id = conversation_id

        message_id = conversation_db.save_message(
            data["user_input"],
            full_response,
            final_conversation_id,
        )

        # Saving in ChromaDB
        chroma_db_path = "data/databases/chroma_db"
        os.makedirs(chroma_db_path, exist_ok=True)
        chroma_client = chromadb.PersistentClient(path=chroma_db_path)
        collection = chroma_client.get_or_create_collection(name="conversations")

        if data["ai_response"]["prompt_type"] == "statement":
            conversation_text = f"{data['user_name']}: {data['user_input']}\n\nStatement Date: {datetime.now().strftime('%d %B %Y')}"
            embedding = data["embedder"].run(conversation_text)

            document = {
                "id": str(uuid.uuid4()),
                "content": conversation_text,
                "embedding": embedding["embedding"],
                "metadata": {
                    "type": "conversation",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            }

            collection.add(
                ids=[document["id"]],
                embeddings=[document["embedding"]],
                documents=[document["content"]],
                metadatas=[document["metadata"]],
            )

        return {
            "conversation_id": conversation_db.get_latest_conversation_id(),
            "conversation_count": conversation_db.get_conversation_count(),
            "message_id": message_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving conversation: {str(e)}")


async def create_conversation_title(
    conversation_id: int, user_message: str, ai_response: str
) -> str:
    """
    Create a conversation title based on user input and AI response.

    Args:
        conversation_id (int): The ID of the conversation in the database.
        user_message (str): The user's input message.
        ai_response (str): The AI's response to the user's message.

    Returns:
        str: The generated conversation title.
    """
    try:
        generator = OpenAIGenerator(model="gpt-4o-mini")

        prompt_template = """
        Create a concise conversation title (max 30 characters) based on the following user message and AI response. Only return the title, don't return any other text.
        User message: {{ user_message }}
        AI response: {{ ai_response }}
        """

        prompt = prompt_template.replace("{{ user_message }}", user_message).replace(
            "{{ ai_response }}", ai_response
        )

        result = generator.run(prompt)
        title = result["replies"][0].strip()

        title = title[:30]

        conversation_db = ConversationDatabase()
        conversation_db.update_conversation_title(
            conversation_id=conversation_id,
            title=title,
        )

        return title

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating conversation title: {str(e)}"
        )
