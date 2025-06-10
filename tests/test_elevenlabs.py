import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from dotenv import load_dotenv
import os
from elevenlabs.client import ElevenLabs
from fastapi import HTTPException
from datetime import datetime
from config.voice_ids import ELEVENLABS_VOICE_IDs

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

async def convert_text_to_speech(answer: str, voice_name: str = "Sarah") -> str:
    """
    Convert text to speech using ElevenLabs
    """
    try:
        if not ELEVENLABS_API_KEY:
            raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY not found in .env file")

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

        audio = client.text_to_speech.convert(
            text=answer,
            voice_id=ELEVENLABS_VOICE_IDs[voice_name],
            model_id="eleven_multilingual_v2"
        )
        
        output_path = f"data/model_outputs/output_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.mp3"
        os.makedirs("data/model_outputs", exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        return output_path

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")

async def test_tts():
    english_test_text = "Test of the ElevenLabs text-to-speech conversion."
    arabic_test_text = "هذا اختبار للنص العربي, هذا اختبار للنص العربي"
    try:
        output_file = await convert_text_to_speech(english_test_text)
        print(f"Audio file generated successfully: {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_tts())