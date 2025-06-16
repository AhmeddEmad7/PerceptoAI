import sys
import os
from typing import Optional
from fastapi import HTTPException
import whisper

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

import re
from num2words import num2words

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
        model = whisper.load_model("medium")  # Adjust model size as needed
        result = model.transcribe(samples, fp16=False)  # Explicitly use FP32 on CPU
        return result["text"]
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")


async def convert_text_to_speech(
    answer: str, prompt: str = None, voice_name: str = "Sarah", input_language:str = "en"
) -> str:
    """
    Convert text to speech using ElevenLabs with basic tone adjustment based on sentiment.
    """
    try:
        if not os.getenv("ELEVENLABS_API_KEY"):
            raise HTTPException(
                status_code=500, detail="ELEVENLABS_API_KEY not found in .env file"
            )
        
        if input_language == "ar":
            western_to_arabic = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
            answer = answer.translate(western_to_arabic)

            # Verbalize decimals (e.g., "31.4" → "واحد وثلاثون وأربعة أعشار")
            def verbalize_decimal(match):
                number = float(match.group(0))
                integer_part = int(number)
                decimal_part = int((number - integer_part) * 10)
                integer_text = num2words(integer_part, lang='ar')
                if decimal_part == 0:
                    return integer_text
                decimal_text = num2words(decimal_part, lang='ar')
                return f"{integer_text} و{decimal_text} أعشار"
            
            answer = re.sub(r'\d+\.\d', verbalize_decimal, answer)
            print(f"Preprocessed Arabic text for TTS: {answer}")

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
    Create a concise title for a conversation based on the user input and AI response.
    """
    try:
        generator = OpenAIGenerator(model="gpt-4o-mini")

        prompt = (
            "Create a concise conversation title (max 50 characters) "
            "based on the following user message and AI response. "
            "Only return the title, don't return any other text.\n"
            f"User message: {user_message}\n"
            f"AI response: {ai_response}"
        )

        result = generator.run(prompt)
        title = result["replies"][0].strip()[:50]  # Ensure max 50 characters

        conversation_db = ConversationDatabase()
        conversation_db.update_conversation_title(conversation_id, title)

        return title

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating conversation title: {str(e)}"
        )
