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

def transcribe_with_whisper(audio_data):
    """Transcribe audio using Whisper AI."""
    try:
        # Create a temporary file for the audio data
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()
            
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            st.info(f"Using device: {device}")
            
            # Load Whisper model
            model = whisper.load_model("base", device=device)
            
            # Transcribe audio
            result = model.transcribe(temp_file.name)
            
            # Clean up
            os.unlink(temp_file.name)
            
            return result["text"]
    except Exception as e:
        st.error(f"Error transcribing with Whisper: {str(e)}")
        return None

def transcribe_with_speech_recognition(audio_data):
    """Transcribe audio using SpeechRecognition."""
    try:
        # Create a temporary file for the audio data
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()
            
            # Initialize recognizer
            recognizer = sr.Recognizer()
            
            # Adjust for ambient noise and transcribe
            with sr.AudioFile(temp_file.name) as source:
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.record(source)
            
            # Perform transcription
            text = recognizer.recognize_google(audio_data)
            
            # Clean up
            os.unlink(temp_file.name)
            
            return text
            
    except sr.UnknownValueError:
        st.error("Speech Recognition could not understand the audio")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Speech Recognition service: {str(e)}")
        return None
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