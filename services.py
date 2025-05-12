from fastapi import HTTPException
import whisper
from gtts import gTTS
from datetime import datetime
import chromadb
from database import ConversationDatabase
from haystack.components.embedders import OpenAITextEmbedder
from haystack_integrations.document_stores.chroma.document_store import ChromaDocumentStore
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
        output_path = f"model_outputs/output_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.mp3"
        tts.save(output_path)
        
        return output_path

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")

def save_conversation(user_input: str, ai_response: dict, embedder: OpenAITextEmbedder, user_name: str, conversation_count_threshold: int) -> int:
    """
    Save conversation to SQLite and non-question inputs to ChromaDB with embeddings
    """
    try:
        chroma_client = chromadb.PersistentClient(path="databases/chroma_db")
        collection = chroma_client.get_or_create_collection(name="conversations")
        
        # Saving in SQLite
        conversation_db = ConversationDatabase()
        _, conversation_count = conversation_db.save_conversation(user_input, ai_response["answer"], conversation_count_threshold)
        
        # Saving in ChromaDB
        if ai_response["prompt_type"] == 'statement':
            conversation_text = f"{user_name}: {user_input}"
            embedding = embedder.run(conversation_text)
            
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