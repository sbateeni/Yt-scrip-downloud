import re
from pytube import YouTube
import streamlit as st
import os
import tempfile
from pydub import AudioSegment
import time

def clean_youtube_url(url):
    """Clean and validate YouTube URL."""
    try:
        # Remove any tracking parameters
        url = re.sub(r'&t=\d+s', '', url)
        url = re.sub(r'&feature=.*', '', url)
        
        # Extract video ID
        video_id = extract_video_id(url)
        if not video_id:
            return None
            
        # Return clean URL
        return f"https://www.youtube.com/watch?v={video_id}"
    except Exception as e:
        st.error(f"Error cleaning URL: {str(e)}")
        return None

def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    try:
        # Regular expression pattern for YouTube video IDs
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard YouTube URL
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',  # Short YouTube URL
            r'(?:embed\/)([0-9A-Za-z_-]{11})'  # Embedded YouTube URL
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    except Exception as e:
        st.error(f"Error extracting video ID: {str(e)}")
        return None

def is_video_available(url):
    """Check if the video is available and accessible."""
    try:
        yt = YouTube(url)
        # Try to access video info
        yt.check_availability()
        return True
    except Exception as e:
        st.error(f"Video is not available: {str(e)}")
        return False

def download_audio(url, video_id, max_retries=3):
    """Download audio from YouTube video with retry mechanism."""
    try:
        # Clean URL
        clean_url = clean_youtube_url(url)
        if not clean_url:
            return None
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize YouTube object
            yt = YouTube(clean_url)
            
            # Get audio stream
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            if not audio_stream:
                st.error("No audio stream found for this video")
                return None
                
            # Set output path
            output_path = os.path.join(temp_dir, f"{video_id}.mp4")
            
            # Download with retry mechanism
            for attempt in range(max_retries):
                try:
                    # Download the audio
                    audio_stream.download(
                        output_path=temp_dir,
                        filename=f"{video_id}.mp4"
                    )
                    
                    # Verify file was downloaded
                    if os.path.exists(output_path):
                        # Convert to WAV format
                        audio = AudioSegment.from_file(output_path)
                        wav_path = os.path.join(temp_dir, f"{video_id}.wav")
                        audio.export(wav_path, format="wav")
                        
                        # Read the WAV file into memory
                        with open(wav_path, 'rb') as f:
                            audio_data = f.read()
                        return audio_data
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        st.warning(f"Download attempt {attempt + 1} failed. Retrying...")
                        time.sleep(2)  # Wait before retrying
                    else:
                        raise e
                        
            return None
            
    except Exception as e:
        st.error(f"Error downloading video: {str(e)}")
        return None 