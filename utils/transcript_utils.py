import whisper
import streamlit as st
import torch
import speech_recognition as sr
import os

def transcribe_with_whisper(audio_path):
    """Transcribe audio using Whisper AI."""
    try:
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        st.info(f"Using device: {device}")
        
        # Load Whisper model
        model = whisper.load_model("base", device=device)
        
        # Transcribe audio
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        st.error(f"Error transcribing with Whisper: {str(e)}")
        return None

def transcribe_with_speech_recognition(audio_path):
    """Transcribe audio using SpeechRecognition."""
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Load audio file
        with sr.AudioFile(audio_path) as source:
            # Read audio data
            audio_data = recognizer.record(source)
            
            # Perform transcription
            text = recognizer.recognize_google(audio_data)
            return text
            
    except Exception as e:
        st.error(f"Error transcribing with SpeechRecognition: {str(e)}")
        return None

def save_transcript(text, video_id, output_dir="transcripts"):
    """Save transcript to a text file."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create file path
        file_path = os.path.join(output_dir, f"transcript_{video_id}.txt")
        
        # Write transcript to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
            
        return file_path
        
    except Exception as e:
        st.error(f"Error saving transcript: {str(e)}")
        return None 