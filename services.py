import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Optional
from fastapi import HTTPException
import whisper
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from datetime import datetime
import chromadb
from database import ConversationDatabase
import uuid
from config.voice_ids import ELEVENLABS_VOICE_IDs

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

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

async def convert_text_to_speech(answer: str, voice_name: str = "Sarah") -> str:
    """
    Convert text to speech using ElevenLabs
    """
    try:
        if not ELEVENLABS_API_KEY:
            raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY not found in .env file")

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

        audio = client.text_to_speech.convert(
            text=answer,
            voice_id=ELEVENLABS_VOICE_IDs[voice_name],
            model_id="eleven_multilingual_v2"
        )
        
        output_path = f"data/model_outputs/output_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.mp3"
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        return output_path

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")

def save_conversation(data: dict, new_conv: Optional[bool] = False) -> int:
    """
    Save conversation to SQLite and non-question inputs to ChromaDB with embeddings
    """
    try:
        # Saving in SQLite
        conversation_db = ConversationDatabase()
        full_response = data["ai_response"]["answer"] + f"\n\nSources Links: {data['ai_response']['url']}" if data['ai_response']['url'] is not None else data['ai_response']['answer']
        conversation_count = conversation_db.save_conversation(data["user_input"], full_response, data["conv_count_threshold"], new_conv)
        
        # Saving in ChromaDB
        chroma_client = chromadb.PersistentClient(path="data/databases/chroma_db")
        collection = chroma_client.get_or_create_collection(name="conversations")

        if data["ai_response"]["prompt_type"] == 'statement':
            conversation_text = f"{data['user_name']}: {data['user_input']}\n\nStatement Date: {datetime.now().strftime('%d %B %Y')}"
            embedding = data["embedder"].run(conversation_text)
            
            document = {
                "id": str(uuid.uuid4()),
                "content": conversation_text,
                "embedding": embedding['embedding'],
                "metadata": {
                    "type": "conversation",
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            collection.add(
                ids=[document["id"]],
                embeddings=[document["embedding"]],
                documents=[document["content"]],
                metadatas=[document["metadata"]]
            )        
        
        return conversation_count
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving conversation: {str(e)}")