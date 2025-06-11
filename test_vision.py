#!/usr/bin/env python3
"""
Test script for PerceptoAI vision capabilities
This script demonstrates how to test the multimodal features
"""

import os
import tempfile
from vision_service import VisionService
from gtts import gTTS
import cv2
import datetime
from datetime import datetime
import sounddevice as sd
from scipy.io.wavfile import write

def create_test_audio(text: str, filename: str = "test_audio.wav"):
    """Create a test audio file from text"""
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(filename)
    return filename

def test_vision_service():
    """Test the vision service directly"""
    print("Testing Vision Service with image + audio...")

    # Step 1: Capture image
    test_image_path = capture_image_from_camera()
    if not test_image_path:
        print("No image was captured.")
        return

    # Step 2: Record audio question
    audio_path = record_audio(duration=5)

    # Step 3: Transcribe audio
    vision_service = VisionService()
    try:
        question = vision_service.transcribe_audio(audio_path)
        print(f"Transcribed Question: {question}")
    except Exception as e:
        print(f"Audio transcription failed: {e}")
        return

    # Step 4: Process image + question
    result = vision_service.process_image_with_query(test_image_path, question)
    if result["success"]:
        print(f"\nAI Answer:\n{result['analysis']}")
    else:
        print(f"Error: {result['error']}")


def create_example_requests():
    """Create example audio files for testing multimodal requests"""
    print("Creating example audio files for testing...")
    
    examples = [
        ("What do you see in this image?", "what_do_you_see.wav"),
        ("Describe this picture to me", "describe_picture.wav"),
        ("What's happening in this photo?", "whats_happening.wav"),
        ("Can you identify the objects in this image?", "identify_objects.wav"),
        ("Tell me about the colors and composition", "colors_composition.wav")
    ]
    
    os.makedirs("test_audio", exist_ok=True)
    
    for text, filename in examples:
        filepath = os.path.join("test_audio", filename)
        create_test_audio(text, filepath)
        print(f"Created: {filepath}")
    
    print("\nExample usage:")
    print("python process_multimodal.py test_audio/what_do_you_see.wav your_image.jpg")


def capture_image_from_camera() -> str:
    """
    Capture an image from the laptop camera using DirectShow backend for Windows compatibility.
    
    Returns:
        str: Path to the captured image
    """
    try:
        # Force DirectShow backend to avoid MSMF issues
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            raise RuntimeError("Could not access the camera. Is it in use by another application?")
        
        print("Camera opened. Press 'c' to capture an image, or 'q' to quit.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                raise RuntimeError("Failed to read from camera.")
            
            cv2.imshow('Live Camera - Press c to capture, q to quit', frame)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('c'):
                os.makedirs("data/captured_images", exist_ok=True)
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                image_path = f"data/captured_images/capture_{timestamp}.jpg"
                cv2.imwrite(image_path, frame)
                print(f"Image saved to {image_path}")
                cap.release()
                cv2.destroyAllWindows()
                return image_path
            elif key == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                raise RuntimeError("Image capture cancelled by user.")
    
    except Exception as e:
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()
        raise RuntimeError(f"Error capturing image: {str(e)}")


def record_audio(duration: int = 5, filename: str = "user_question.wav") -> str:
    """
    Record audio from the microphone for a given duration.

    Args:
        duration (int): Duration in seconds
        filename (str): Output WAV file name

    Returns:
        str: Path to saved audio file
    """
    fs = 44100  # Sample rate
    print(f"Recording for {duration} seconds...")

    try:
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  # Wait for the recording to finish
        write(filename, fs, audio)
        print(f"Audio saved to {filename}")
        return filename
    except Exception as e:
        raise RuntimeError(f"Failed to record audio: {str(e)}")



def main():
    print("PerceptoAI Vision Testing Tool")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Test Vision Service directly")
        print("2. Create example audio files")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            test_vision_service()
        elif choice == "2":
            create_example_requests()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
