import io
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
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

load_dotenv()
app = FastAPI(title="PerceptoAI RAG Pipeline")


@app.get("/")
async def root():
    return {"message": "PerceptoAI server is running!"}


@app.post("/process_audio")
async def process_audio(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    new_conv: Optional[bool] = Query(False, description="Start a new conversation"),
    voice: Optional[str] = Query("Sarah", description="Voice to use for the response"),
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
        audio_response = await convert_text_to_speech(response["answer"], prompt, voice)

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


if __name__ == "__main__":
    uvicorn.run(app)
