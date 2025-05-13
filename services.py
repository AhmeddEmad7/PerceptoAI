from typing import Optional
from fastapi import HTTPException
import whisper
from gtts import gTTS
from datetime import datetime
import chromadb
from database import ConversationDatabase
import uuid

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

async def convert_text_to_speech(answer: str) -> str:
    """
    Convert text to speech using gTTS (Google Text-to-Speech)
    """
    try:
        tts = gTTS(text=answer, lang='en', slow=False, tld='fr')
        output_path = f"data/model_outputs/output_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.mp3"
        tts.save(output_path)
        
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
        full_response = data["ai_response"]["answer"] + f"\n\nSource Link: {data['ai_response']['url']}" if data['ai_response']['url'] is not None else data['ai_response']['answer']
        conversation_count = conversation_db.save_conversation(data["user_input"], full_response, data["conv_count_threshold"], new_conv)
        
        # Saving in ChromaDB
        chroma_client = chromadb.PersistentClient(path="data/databases/chroma_db")
        collection = chroma_client.get_or_create_collection(name="conversations")

        if data["ai_response"]["prompt_type"] == 'statement':
            conversation_text = f"{data['user_name']}: {data['user_input']}"
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