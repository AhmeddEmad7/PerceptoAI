import base64
import os
from openai import OpenAI
from PIL import Image
import io
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class VisionService:
    """
    Service for processing images using GPT-4 Vision API
    and transcribing audio using Whisper.
    """
    
    def __init__(self):
        self.client = OpenAI(
            api_key='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'
        )
        
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image to base64 string for GPT-4 Vision API
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Base64 encoded image string
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Error encoding image: {str(e)}")
    
    def process_image_with_query(self, image_path: str, user_query: str = None) -> Dict[str, Any]:
        """
        Process image with GPT-4 Vision and answer user's question
        
        Args:
            image_path (str): Path to the image file
            user_query (str): User's question about the image
            
        Returns:
            Dict containing image analysis results
        """
        try:
            # Encode image to base64
            base64_image = self.encode_image_to_base64(image_path)
            
            # Determine the image format
            image_format = self._get_image_format(image_path)
            
            # Create the prompt based on whether there's a specific query
            if user_query and len(user_query.strip()) > 0:
                # User has a specific question about the image
                prompt = f"""The user is asking about this image: "{user_query}"
                
Please analyze the image and answer their question directly. Also provide:
1. A brief description of what you see in the image
2. Any relevant context that might be helpful
3. Answer to their specific question

Be conversational and natural in your response."""
            else:
                # General image analysis
                prompt = """Please analyze this image and provide:
1. A detailed description of what you see
2. Any notable objects, people, or scenes
3. The setting or context (indoor/outdoor, time of day if visible, etc.)
4. Any interesting details or observations
5. Potential activities or purposes related to what's shown

Be descriptive and conversational in your response."""
            
            # Make API call to GPT-4 Vision
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o which has vision capabilities
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_format};base64,{base64_image}",
                                    "detail": "high"  # High detail for better analysis
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": analysis,
                "image_processed": True,
                "model_used": "gpt-4o",
                "user_query": user_query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process image: {str(e)}",
                "image_processed": False
            }
    
    def _get_image_format(self, image_path: str) -> str:
        """
        Determine the image format from file extension
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Image format (jpeg, png, etc.)
        """
        try:
            with Image.open(image_path) as img:
                format_name = img.format.lower()
                if format_name == 'jpeg':
                    return 'jpeg'
                elif format_name == 'png':
                    return 'png'
                elif format_name == 'webp':
                    return 'webp'
                elif format_name == 'gif':
                    return 'gif'
                else:
                    return 'jpeg'  # Default fallback
        except Exception:
            return 'jpeg'  # Default fallback
    
    def generate_image_context(self, image_path: str, user_query: str = None) -> str:
        """
        Generate contextual information about the image for RAG pipeline
        
        Args:
            image_path (str): Path to the image file
            user_query (str): User's question about the image
            
        Returns:
            str: Formatted context string for RAG pipeline
        """
        result = self.process_image_with_query(image_path, user_query)
        
        if result["success"]:
            context = f"""
IMAGE ANALYSIS:
{result['analysis']}

[Image processed using {result['model_used']}]
"""
            if user_query:
                context = f"User's question about the image: {user_query}\n" + context
                
            return context
        else:
            return f"[Error processing image: {result['error']}]"

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio using OpenAI Whisper.

        Args:
            audio_path (str): Path to the WAV file

        Returns:
            str: Transcribed text
        """
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                return transcript.text
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")
