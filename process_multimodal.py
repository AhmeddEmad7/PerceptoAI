import requests
import sys
import os
from pathlib import Path

def send_multimodal_request(audio_file_path: str, image_file_path: str = None):
    """
    Send audio and optional image to the PerceptoAI API
    
    Args:
        audio_file_path (str): Path to the audio file
        image_file_path (str): Optional path to the image file
    """
    
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file '{audio_file_path}' not found.")
        return
    
    if image_file_path and not os.path.exists(image_file_path):
        print(f"Error: Image file '{image_file_path}' not found.")
        return
    
    files = {}
    
    try:
        # Add audio file
        with open(audio_file_path, 'rb') as audio_file:
            files['file'] = ('audio.wav', audio_file, 'audio/wav')
            
            # Add image file if provided
            if image_file_path:
                with open(image_file_path, 'rb') as image_file:
                    # Determine MIME type based on extension
                    ext = Path(image_file_path).suffix.lower()
                    if ext in ['.jpg', '.jpeg']:
                        mime_type = 'image/jpeg'
                    elif ext == '.png':
                        mime_type = 'image/png'
                    elif ext == '.gif':
                        mime_type = 'image/gif'
                    elif ext == '.webp':
                        mime_type = 'image/webp'
                    else:
                        mime_type = 'image/jpeg'  # Default
                    
                    files['image'] = (os.path.basename(image_file_path), image_file, mime_type)
            
            # Send request to API
            response = requests.post('http://localhost:8000/process_audio', files=files)
            
            if response.status_code == 200:
                result = response.json()
                
                print("=" * 50)
                print("PerceptoAI Response")
                print("=" * 50)
                print(f"Transcribed Text: {result['transcription']}")
                print(f"Prompt Type: {result['prompt_type']}")
                print(f"AI Response: {result['response']}")
                
                if result.get('image_processed'):
                    print(f"Image Processed: Yes")
                    print(f"Image Path: {result.get('image_path', 'N/A')}")
                    if result.get('vision_analysis'):
                        print(f"Vision Analysis: {result['vision_analysis']}")
                else:
                    print(f"Image Processed: No")
                
                # Save audio response if available
                if result.get('audio_response'):
                    audio_output_path = f"response_{os.path.basename(audio_file_path)}.mp3"
                    print(f"Audio response saved to: {audio_output_path}")
                    # Note: In a real implementation, you'd need to handle the audio response properly
                
            else:
                print(f"Error: {response.status_code}")
                print(f"Details: {response.text}")
                
    except Exception as e:
        print(f"Failed to send request: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python process_multimodal.py <audio_file> [image_file]")
        print("\nExamples:")
        print("  python process_multimodal.py data/audio_prompts/weather.wav")
        print("  python process_multimodal.py data/audio_prompts/weather.wav photo.jpg")
        print("  python process_multimodal.py recording.wav screenshot.png")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    image_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Sending request with:")
    print(f"  Audio: {audio_path}")
    print(f"  Image: {image_path if image_path else 'None'}")
    print()
    
    send_multimodal_request(audio_path, image_path)

if __name__ == "__main__":
    main()
