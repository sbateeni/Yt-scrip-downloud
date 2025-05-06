import re
import yt_dlp
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
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'ignoreerrors': True,
            'cookiesfrombrowser': ('chrome',),  # Try to use Chrome cookies
            'cookiefile': 'cookies.txt'  # Fallback to cookies file
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return False
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
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
                'outtmpl': os.path.join(temp_dir, f'{video_id}.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'cookiesfrombrowser': ('chrome',),  # Try to use Chrome cookies
                'cookiefile': 'cookies.txt',  # Fallback to cookies file
                'extract_flat': False,
                'ignoreerrors': True,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'geo_verification_proxy': None,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            }
            
            # Download with retry mechanism
            for attempt in range(max_retries):
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([clean_url])
                    
                    # Find the downloaded file
                    wav_file = os.path.join(temp_dir, f'{video_id}.wav')
                    if os.path.exists(wav_file):
                        # Read the WAV file into memory
                        with open(wav_file, 'rb') as f:
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