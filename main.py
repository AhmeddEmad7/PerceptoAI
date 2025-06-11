import io
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from database import ConversationDatabase
from services import (
    convert_audio_to_text,
    convert_text_to_speech,
    create_conversation_title,
    save_conversation,
)
from rag_pipeline import RAGPipeline
from summarizer import ConversationSummarizer
from dotenv import load_dotenv
from rag_config import USER_NAME, CONVERSATION_COUNT_THRESHOLD
from typing import Optional
from fastapi import Query
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI(title="PerceptoAI RAG Pipeline")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "PerceptoAI server is running!"}


@app.post("/process_audio")
async def process_audio(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    new_conv: Optional[bool] = Query(False, description="Start a new conversation"),
):
    try:
        rag_pipeline = RAGPipeline(user_name=USER_NAME)
        conversation_summarizer = ConversationSummarizer(rag_pipeline)

        # Read audio data into memory
        audio_data = await file.read()

        # Validate file format
        allowed_extensions = {".wav", ".mp3", ".m4a"}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Create a BytesIO object for in-memory processing
        audio_buffer = io.BytesIO(audio_data)
        audio_buffer.name = file.filename  # Set filename for compatibility

        # Process audio directly from memory
        prompt = await convert_audio_to_text(
            audio_buffer, file_ext[1:]
        )  # Pass file extension
        response = rag_pipeline.process_query(prompt)
        conversations_db = ConversationDatabase()
        audio_response = await convert_text_to_speech(
            response["answer"], prompt, conversations_db.get_current_voice()
        )

        conversations_data = save_conversation(
            {
                "user_input": prompt,
                "ai_response": response,
                "embedder": rag_pipeline.embedder,
                "user_name": USER_NAME,
                "conv_count_threshold": CONVERSATION_COUNT_THRESHOLD,
            },
            new_conv,
        )

        print(
            "Number of conversations processed:",
            conversations_data["conversation_count"],
        )
        background_tasks.add_task(
            conversation_summarizer.process_conversation,
            conversations_data["conversation_count"],
            CONVERSATION_COUNT_THRESHOLD,
        )

        if new_conv:
            background_tasks.add_task(
                create_conversation_title,
                conversations_data["conversation_id"],
                prompt,
                response["answer"],
            )

        return {
            "transcription": prompt,
            "prompt_type": response["prompt_type"],
            "response": response["answer"],
            "audio_response": audio_response,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")


@app.get("/voice")
def get_voice():
    conversations_db = ConversationDatabase()
    return {"voice": conversations_db.get_current_voice()}


@app.put("/voice")
def update_voice(voice: str):
    if not voice:
        raise HTTPException(status_code=400, detail="Voice cannot be empty")

    allowed_voices = ["Bella", "Antoni", "Elli", "Josh", "Sarah", "Brian"]
    if voice not in allowed_voices:
        raise HTTPException(
            status_code=400, detail=f"Invalid voice. Allowed voices: {allowed_voices}"
        )

    conversations_db = ConversationDatabase()
    conversations_db.update_current_voice(voice)
    return {"message": f"Voice updated to {voice}"}


@app.get("/conversations")
async def get_conversations():
    try:
        conversations_db = ConversationDatabase()
        return conversations_db.get_conversations()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching conversations: {str(e)}"
        )


@app.get("/conversations/{conversation_id}")
async def get_conversation_messages(
    conversation_id: int,
):
    try:
        conversations_db = ConversationDatabase()
        return conversations_db.get_messages_from_conversation(conversation_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching conversation: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app)
