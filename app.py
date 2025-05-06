import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re
import validators
from pytube import YouTube
import whisper
import os
import tempfile
import time

def extract_video_id(url):
    # Regular expressions for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/watch\?.*&v=)([^&\n?#]+)',
        r'youtube\.com\/shorts\/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        return formatter.format_transcript(transcript)
    except Exception as e:
        return None

def download_audio(url, video_id):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the audio file
            audio_path = audio_stream.download(output_path=temp_dir)
            return audio_path
    except Exception as e:
        st.error(f"Error downloading audio: {str(e)}")
        return None

def transcribe_with_whisper(audio_path):
    try:
        # Load Whisper model
        model = whisper.load_model("base")
        
        # Transcribe audio
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        st.error(f"Error transcribing with Whisper: {str(e)}")
        return None

# Set page configuration
st.set_page_config(
    page_title="YouTube Transcript Extractor",
    page_icon="🎥",
    layout="centered"
)

# Add title and description
st.title("🎥 YouTube Transcript Extractor")
st.markdown("""
This application extracts transcripts from YouTube videos using two methods:
1. YouTube's built-in transcripts (if available)
2. AI-powered speech recognition (Whisper) as a fallback
""")

# Input field for YouTube URL
url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    if not validators.url(url):
        st.error("Please enter a valid URL")
    else:
        video_id = extract_video_id(url)
        
        if video_id:
            st.info("Video ID detected! Processing...")
            
            # Try to get YouTube transcript first
            transcript = get_youtube_transcript(video_id)
            
            if transcript:
                st.success("Transcript successfully extracted using YouTube's built-in transcripts!")
                st.text_area("Transcript:", transcript, height=400)
                
                # Add download button
                st.download_button(
                    label="Download Transcript",
                    data=transcript,
                    file_name=f"transcript_{video_id}.txt",
                    mime="text/plain"
                )
            else:
                st.warning("No built-in transcript available. Attempting to generate transcript using AI...")
                
                with st.spinner("Downloading audio and generating transcript (this may take a few minutes)..."):
                    # Download audio
                    audio_path = download_audio(url, video_id)
                    
                    if audio_path:
                        # Transcribe with Whisper
                        transcript = transcribe_with_whisper(audio_path)
                        
                        if transcript:
                            st.success("Transcript successfully generated using AI!")
                            st.text_area("Transcript:", transcript, height=400)
                            
                            # Add download button
                            st.download_button(
                                label="Download Transcript",
                                data=transcript,
                                file_name=f"transcript_{video_id}.txt",
                                mime="text/plain"
                            )
        else:
            st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.")

# Add footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Whisper") 