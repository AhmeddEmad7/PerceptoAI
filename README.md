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

2. Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

3. Run the FastAPI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- POST `/process_audio`: Process audio input and get AI response
  - Accepts: Audio file (WAV format)
  - Returns: Transcription, AI response, and audio response

## Project Structure

- `main.py`: FastAPI application and RAG pipeline
- `database.py`: SQLite database operations
- `requirements.txt`: Project dependencies
- `.env.example`: Environment variable template

## Dependencies

- Haystack: For RAG pipeline implementation
- FastAPI: Web framework
- ChromaDB: Vector database for memory storage
- SQLite: Local database for conversation history
- SoundDevice: Audio input/output handling
