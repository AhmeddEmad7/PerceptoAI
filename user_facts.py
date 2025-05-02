import chromadb
from datetime import datetime
from fastapi import HTTPException
from haystack.components.embedders import OpenAITextEmbedder
from dotenv import load_dotenv

load_dotenv()
chroma_client = chromadb.PersistentClient(path="databases/chroma_db")
collection = chroma_client.get_or_create_collection(name="conversations")

def add_user_facts():
    try:
        embedder = OpenAITextEmbedder()
        facts = [
            "Ahmed is a male, married, and the father of two children.",
            "Ahmed is 44 years old and was born on February 2, 1979.",
            "Mother's name is Scarlet.",
            "Father's name is John."
            "Ahmed has a Bachelor of Science in Computer Science from the University of California, Berkeley."
            "Ahmed works as a software engineer specializing in AI and machine learning.",
            "Ahmed has experience with Python, FastAPI, and Haystack framework.",
            "Ahmed is interested in natural language processing and computer vision.",
            "Ahmed is currently working on a voice-activated AI assistant project.",
            "Ahmed enjoys solving complex problems with AI solutions.",
        ]
        
        embeddings = [embedder.run(fact) for fact in facts]
        documents = []
        for i, fact in enumerate(facts):
            documents.append({
                "id": f"fact_{i}",
                "content": fact,
                "embedding": embeddings[i]['embedding'],
                "metadata": {
                    "category": "user_profile",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            })
        
        collection.add(
            ids=[doc["id"] for doc in documents],
            embeddings=[doc["embedding"] for doc in documents],
            documents=[doc["content"] for doc in documents],
            metadatas=[doc["metadata"] for doc in documents]
        )
        
        print("User facts added to ChromaDB successfully!")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding user facts: {str(e)}")

add_user_facts()