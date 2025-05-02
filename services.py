from fastapi import HTTPException
import whisper
from gtts import gTTS
from datetime import datetime
import chromadb
from database import ConversationDatabase
from haystack.components.embedders import OpenAITextEmbedder

chroma_client = chromadb.PersistentClient(path="databases/chroma_db")
collection = chroma_client.get_or_create_collection(name="conversations")

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

def save_conversation(user_input: str, ai_response: dict) -> int:
    """
    Save conversation to SQLite and non-question inputs to ChromaDB with embeddings
    """
    try:
        # Saving in SQLite
        conversation_db = ConversationDatabase()
        conversation_id = conversation_db.save_conversation(user_input, ai_response["answer"])
        
        # Saving in ChromaDB
        if ai_response["prompt_type"] == 'statement':
            embedder = OpenAITextEmbedder()
            conversation_text = f"User: {user_input}\nAI: {ai_response['answer']}"
            embedding = embedder.run(conversation_text)
            
            document = {
                "id": str(conversation_id),
                "content": conversation_text,
                "embedding": embedding['embedding'],
                "metadata": {
                    "user_input": user_input,
                    "ai_response": ai_response["answer"],
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            # Add document to ChromaDB
            collection.add(
                ids=[document["id"]],
                embeddings=[document["embedding"]],
                documents=[document["content"]],
                metadatas=[document["metadata"]]
            )      
        return conversation_id
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving conversation: {str(e)}")