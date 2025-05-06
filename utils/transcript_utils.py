from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import whisper
import streamlit as st
import torch

def get_youtube_transcript(video_id):
    """Get transcript from YouTube's built-in transcript system."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        return formatter.format_transcript(transcript)
    except Exception as e:
        return None

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