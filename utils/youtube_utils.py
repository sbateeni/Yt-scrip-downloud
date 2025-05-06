import re
from pytube import YouTube
import tempfile
import streamlit as st
import requests
from urllib.parse import parse_qs, urlparse

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

def get_video_info(url):
    """Get video information using pytube."""
    try:
        yt = YouTube(url)
        return yt
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
        return None

def download_audio(url, video_id):
    """Download audio from YouTube video with multiple fallback options."""
    try:
        # First attempt: Try pytube
        yt = get_video_info(url)
        if not yt:
            return None

        # Get all audio streams
        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
        
        if not audio_streams:
            st.error("No audio streams found for this video")
            return None

        # Try different audio streams until one works
        for stream in audio_streams:
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    st.info(f"Attempting to download audio with quality: {stream.abr}kbps")
                    audio_path = stream.download(output_path=temp_dir)
                    if audio_path:
                        return audio_path
            except Exception as e:
                st.warning(f"Failed to download with quality {stream.abr}kbps: {str(e)}")
                continue

        st.error("All download attempts failed")
        return None

    except Exception as e:
        st.error(f"Error in download_audio: {str(e)}")
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