import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from services import convert_audio_to_text, convert_text_to_speech, save_conversation
from rag_pipeline import RAGPipeline
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PerceptoAI RAG Pipeline")
rag_pipeline = RAGPipeline()

@app.get("/")
async def root():
    return {"message": "PerceptoAI server is running!"}

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    try:

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            prompt = await convert_audio_to_text(temp_file.name)
            response = rag_pipeline.process_query(prompt)
            audio_response = await convert_text_to_speech(response["answer"])

            save_conversation(prompt, response)

            return {
                "transcription": prompt,
                "prompt_type": response["prompt_type"],
                "response": response["answer"],
                "audio_response": audio_response
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app)
