import re
from pytube import YouTube
import tempfile
import streamlit as st
import requests
from urllib.parse import parse_qs, urlparse
from moviepy.editor import VideoFileClip
import os
from pydub import AudioSegment

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

def download_video(url, video_id):
    """Download video from YouTube."""
    try:
        yt = get_video_info(url)
        if not yt:
            return None

        # Get the best video stream
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not video_stream:
            st.error("No video stream found")
            return None

        with tempfile.TemporaryDirectory() as temp_dir:
            st.info("Downloading video...")
            video_path = video_stream.download(output_path=temp_dir)
            return video_path

    except Exception as e:
        st.error(f"Error downloading video: {str(e)}")
        return None

def extract_audio_from_video(video_path, output_format='wav'):
    """Extract audio from video file and convert to specified format."""
    try:
        # Create temporary directory for audio file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract audio using moviepy
            video = VideoFileClip(video_path)
            audio_path = os.path.join(temp_dir, f"audio.{output_format}")
            
            # Extract audio
            video.audio.write_audiofile(audio_path)
            
            # Close video file
            video.close()
            
            return audio_path

    except Exception as e:
        st.error(f"Error extracting audio: {str(e)}")
        return None

def convert_audio_format(input_path, output_format='wav'):
    """Convert audio file to specified format using pydub."""
    try:
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        # Create temporary directory for converted file
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, f"converted.{output_format}")
            
            # Export audio in new format
            audio.export(output_path, format=output_format)
            
            return output_path

    except Exception as e:
        st.error(f"Error converting audio format: {str(e)}")
        return None

def download_audio(url, video_id):
    """Download and process audio from YouTube video."""
    try:
        # First download the video
        video_path = download_video(url, video_id)
        if not video_path:
            return None

        # Extract audio from video
        audio_path = extract_audio_from_video(video_path)
        if not audio_path:
            return None

        # Convert to WAV format if needed
        if not audio_path.endswith('.wav'):
            audio_path = convert_audio_format(audio_path, 'wav')

        return audio_path

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