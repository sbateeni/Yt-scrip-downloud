import re
from pytube import YouTube
import tempfile
import streamlit as st
import requests
from urllib.parse import parse_qs, urlparse
from moviepy.editor import VideoFileClip
import os
from pydub import AudioSegment
import time

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

def download_audio(url, video_id, max_retries=3):
    """Download audio from YouTube video with retry mechanism."""
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize YouTube object
            yt = YouTube(url)
            
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