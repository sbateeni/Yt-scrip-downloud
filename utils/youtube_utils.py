import re
from pytube import YouTube
import tempfile
import streamlit as st

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/watch\?.*&v=)([^&\n?#]+)',
        r'youtube\.com\/shorts\/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def download_audio(url, video_id):
    """Download audio from YouTube video."""
    try:
        yt = YouTube(url)
        # Get the best audio stream
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        
        if not audio_stream:
            st.error("No audio stream found for this video")
            return None
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the audio file
            audio_path = audio_stream.download(output_path=temp_dir)
            return audio_path
    except Exception as e:
        st.error(f"Error downloading audio: {str(e)}")
        return None 