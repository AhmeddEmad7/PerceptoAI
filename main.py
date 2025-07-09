import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Response
from backend.database import ConversationDatabase
from backend.services import (
    convert_audio_to_text,
    convert_text_to_speech,
    create_conversation_title,
    save_conversation,
)
from backend.rag_pipeline import RAGPipeline
from backend.summarizer import ConversationSummarizer
from dotenv import load_dotenv
from backend.rag_config import USER_NAME, CONVERSATION_COUNT_THRESHOLD
from typing import Optional
from fastapi import Query
import os
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import base64

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
    conversation_id: Optional[int] = Query(None, description="Current conversation ID")
):
    try:
        rag_pipeline = RAGPipeline(user_name=USER_NAME)
        conversation_summarizer = ConversationSummarizer(rag_pipeline)

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            audio_data = await file.read()
            temp_file.write(audio_data)
            temp_file.flush()

        prompt = await convert_audio_to_text(temp_file.name)
        response = rag_pipeline.process_query(prompt)
        conversations_db = ConversationDatabase()
        current_voice = conversations_db.get_current_voice()
        audio_response = await convert_text_to_speech(
            response["answer"], prompt, current_voice
        )

        with open(audio_response, "rb") as f:
            audio_content = f.read()
        os.unlink(audio_response)
        encoded_audio = base64.b64encode(audio_content).decode('utf-8')

        conversations_data = save_conversation(
            {
                "user_input": prompt,
                "ai_response": response,
                "embedder": rag_pipeline.embedder,
                "user_name": USER_NAME,
            },
            conversation_id=conversation_id
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

        # Check if the conversation needs a title (i.e., if it's a new conversation without one)
        current_conversation_id = conversations_data["conversation_id"]
        if current_conversation_id is not None:
            conversations_db = ConversationDatabase()
            conversation_details = conversations_db.get_conversation_details(current_conversation_id)
            if conversation_details and conversation_details["title"] is None:
                background_tasks.add_task(
                    create_conversation_title,
                    current_conversation_id,
                    prompt,
                    response["answer"],
                )
        

        return {
            "transcription": prompt,
            "prompt_type": response["prompt_type"],
            "response": response["answer"],
            "audio_response_base64": encoded_audio,
            "voice": current_voice,
            "conversation_id": conversations_data["conversation_id"],
            "message_id": conversations_data["message_id"],
        }

    except HTTPException as http_exc:
        print(f"ERROR: HTTPException in process_audio: {http_exc.detail}")


@app.post("/conversations")
async def create_new_conversation():
    try:
        conversations_db = ConversationDatabase()
        new_conv_id = conversations_db.create_new_conversation()
        return {"conversation_id": new_conv_id, "message": "New conversation created"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating new conversation: {str(e)}"
        )


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
