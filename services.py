import sys
import os
from typing import Optional
from fastapi import HTTPException
import whisper

# from gtts import gTTS
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from datetime import datetime
import chromadb
from database import ConversationDatabase
import uuid
from textblob import TextBlob
from config.elevenlabs_voice_config import ELEVENLABS_VOICE_IDs, TONE_SETTINGS
import numpy as np
from pydub import AudioSegment
from io import BytesIO

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


async def convert_audio_to_text(audio_input: BytesIO, file_format: str) -> str:
    try:
        # Load audio from BytesIO using pydub
        audio = AudioSegment.from_file(audio_input, format=file_format)

        # Convert to WAV and get samples as NumPy array
        # Ensure mono channel and 16kHz sample rate for Whisper compatibility
        audio = audio.set_channels(1).set_frame_rate(16000)
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        samples /= np.iinfo(audio.array_type).max  # Normalize to [-1.0, 1.0]

        # Load Whisper model and transcribe
        model = whisper.load_model("base")  # Adjust model size as needed
        result = model.transcribe(samples, fp16=False)  # Explicitly use FP32 on CPU
        return result["text"]
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")


async def convert_text_to_speech(
    answer: str, prompt: str = None, voice_name: str = "Sarah"
) -> str:
    """
    Convert text to speech using ElevenLabs with basic tone adjustment based on sentiment.
    """
    try:
        if not os.getenv("ELEVENLABS_API_KEY"):
            raise HTTPException(
                status_code=500, detail="ELEVENLABS_API_KEY not found in .env file"
            )

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
        client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

        audio = client.text_to_speech.convert(
            text=answer,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            voice_settings=TONE_SETTINGS[tone],
        )

        output_path = f"data/model_outputs/output_{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.mp3"
        os.makedirs("data/model_outputs", exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        return output_path

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating speech: {str(e)}"
        )


def save_conversation(data: dict, new_conv: Optional[bool] = False) -> int:
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

        latest_conversation_id = conversation_db.get_latest_conversation_id()
        if new_conv or latest_conversation_id is None:
            conversation_id = None
        else:
            conversation_id = latest_conversation_id

        conversation_db.save_message(
            data["user_input"],
            full_response,
            conversation_id,
        )

        # Saving in ChromaDB
        chroma_client = chromadb.PersistentClient(path="data/databases/chroma_db")
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
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error saving conversation: {str(e)}"
        )


from haystack.components.generators.openai import OpenAIGenerator


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

    Raises:
        HTTPException: If title generation or database update fails.
    """
    try:
        # Initialize OpenAI generator
        generator = OpenAIGenerator(model="gpt-4o-mini")

        # Define a simple prompt for title generation
        prompt_template = """
        Create a concise conversation title (max 50 characters) based on the following user message and AI response. Only return the title, don't return any other text.
        User message: {{ user_message }}
        AI response: {{ ai_response }}
        """

        # Build the prompt
        prompt = prompt_template.replace("{{ user_message }}", user_message).replace(
            "{{ ai_response }}", ai_response
        )

        # Generate the title
        result = generator.run(prompt)
        title = result["replies"][0].strip()

        # Ensure title is within 50 characters
        title = title[:50]

        # Update the conversation title in the database
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
