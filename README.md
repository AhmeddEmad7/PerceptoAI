# PerceptoAI - Smart AI Assistant

PerceptoAI is a smart AI assistant powered by a Raspberry Pi that uses voice input and output for natural conversation.

## Features

- Voice-to-text transcription using Speech-to-Text API
- Context-aware responses using DeepSeek API
- Text-to-speech conversion for AI responses
- Local conversation storage with SQLite
- Vector-based memory storage using ChromaDB
- FastAPI backend service

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Fill in your API keys in `.env` :
```bash
echo "DEEPSEEK_API_KEY=<deepseek_api_key>" >> .env
echo "OPENAI_API_KEY=<openai_api_key>" >> .env
```

3. Add user facts to ChromaDB:
```bash
python add_user_facts.py
```

4. Run the FastAPI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

5. Test the API:
```bash
python process_audio.py
```


## API Endpoints

- GET `/`: Returns a welcome message

- POST `/process_audio`: Process audio input and get AI response
  - Accepts: Audio file (any format)
  - Returns: Transcription, AI response, and audio response

## Project Structure

#### Files:
- `rag_pipeline.py`: RAG pipeline implementation
- `services.py`: Audio processing services
- `database.py`: SQLite database operations
- `process_audio.py`: Audio processing script by sending audio to endpoint
- `add_user_facts.py`: Script for adding user facts to ChromaDB
- `main.py`: FastAPI application with RAG pipeline
- `requirements.txt`: Project dependencies
- `.env`: Environment variables and API keys

#### Directories:
- `model_outputs/`: Directory for storing generated audio responses
- `audio_prompts/`: Directory for storing audio prompts
- `databases/`: Directory for storing database files

## Technologies

- FastAPI: Web framework
- Haystack: For RAG pipeline implementation
- ChromaDB: Vector database for memory storage
- SQLite: Local database for conversation history
- SoundDevice: Audio input/output handling
- Whisper: Speech-to-text transcription
- gTTS: Text-to-speech conversion