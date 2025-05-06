import whisper
import streamlit as st
import torch
import speech_recognition as sr
import os
import tempfile
import io
from pydub import AudioSegment

def convert_to_wav(audio_path):
    """Convert audio file to WAV format."""
    try:
        # Get file extension
        _, ext = os.path.splitext(audio_path)
        if ext.lower() == '.wav':
            return audio_path
            
        # Convert to WAV
        audio = AudioSegment.from_file(audio_path)
        wav_path = audio_path.replace(ext, '.wav')
        audio.export(wav_path, format='wav')
        return wav_path
    except Exception as e:
        st.error(f"Error converting audio to WAV: {str(e)}")
        return None

def transcribe_with_whisper(audio_path):
    """Transcribe audio using OpenAI's Whisper model."""
    try:
        # Load Whisper model
        model = whisper.load_model("base")
        
        # Transcribe audio
        result = model.transcribe(audio_path)
        
        if result and "text" in result:
            return result["text"]
        else:
            st.error("Failed to generate transcript with Whisper")
            return None
            
    except Exception as e:
        st.error(f"Error in Whisper transcription: {str(e)}")
        return None

def transcribe_with_google(audio_path):
    """Transcribe audio using Google Speech Recognition."""
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Load audio file
        with sr.AudioFile(audio_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            # Record audio
            audio = recognizer.record(source)
            
        # Transcribe audio
        text = recognizer.recognize_google(audio)
        return text
        
    except sr.UnknownValueError:
        st.error("Google Speech Recognition could not understand the audio")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error in Google Speech Recognition: {str(e)}")
        return None

def save_transcript(transcript, title):
    """Save transcript to a file."""
    try:
        # Create transcripts directory if it doesn't exist
        os.makedirs("transcripts", exist_ok=True)
        
        # Create filename from title
        filename = f"transcripts/{title.lower().replace(' ', '_')}.txt"
        
        # Save transcript
        with open(filename, "w", encoding="utf-8") as f:
            f.write(transcript)
            
        return filename
    except Exception as e:
        st.error(f"Error saving transcript: {str(e)}")
        return None 