import streamlit as st
import validators
import sys
import os
import tempfile

# Import utility functions
from utils.youtube_utils import extract_video_id, download_audio, is_video_available
from utils.youtube_transcript import get_youtube_transcript, get_available_languages, get_transcript_in_language
from utils.transcript_utils import (
    transcribe_with_whisper,
    transcribe_with_speech_recognition,
    save_transcript
)
from utils.system_utils import verify_installation

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'error' not in st.session_state:
    st.session_state.error = None
if 'available_languages' not in st.session_state:
    st.session_state.available_languages = []
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'current_video_id' not in st.session_state:
    st.session_state.current_video_id = None

# Cache only the audio download function
@st.cache_data(ttl=3600)  # Cache for 1 hour
def cached_download_audio(url, video_id):
    return download_audio(url, video_id)

def main():
    # Set page configuration
    st.set_page_config(
        page_title="YouTube Transcript Extractor",
        page_icon="🎥",
        layout="centered"
    )

    # Add title and description
    st.title("🎥 YouTube Transcript Extractor")
    st.markdown("""
    This application extracts transcripts from YouTube videos or audio files using multiple methods:
    1. YouTube's built-in transcripts (if available)
    2. AI-powered speech recognition (Whisper)
    3. Google Speech Recognition
    """)

    # Verify installation
    if not verify_installation():
        st.error("Failed to verify or install required components. Please try refreshing the page.")
        return

    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["YouTube Video", "Audio File"])

    with tab1:
        st.header("YouTube Video Transcription")
        # Input field for YouTube URL
        url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

        # Add transcription method selection
        transcription_method = st.radio(
            "Select transcription method:",
            ["YouTube Built-in", "Whisper AI", "Google Speech Recognition"],
            index=0
        )

        # Add convert button
        convert_button = st.button("Convert to Transcript", disabled=st.session_state.processing)

        if url and convert_button and not st.session_state.processing:
            process_youtube_video(url, transcription_method)

    with tab2:
        st.header("Audio File Transcription")
        # File uploader
        uploaded_file = st.file_uploader("Upload an audio file", type=['mp3', 'wav', 'm4a', 'ogg'])

        # Add transcription method selection for audio file
        audio_transcription_method = st.radio(
            "Select transcription method:",
            ["Whisper AI", "Google Speech Recognition"],
            index=0
        )

        # Add convert button for audio file
        audio_convert_button = st.button("Convert Audio to Transcript", disabled=st.session_state.processing)

        if uploaded_file and audio_convert_button and not st.session_state.processing:
            process_audio_file(uploaded_file, audio_transcription_method)

    # Add footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit and various transcription tools")

def process_youtube_video(url, transcription_method):
    """Process YouTube video for transcription."""
    try:
        st.session_state.processing = True
        st.session_state.error = None

        if not validators.url(url):
            st.error("Please enter a valid URL")
            return

        # Check if video is available
        if not is_video_available(url):
            st.error("This video is not available or is restricted")
            return

        video_id = extract_video_id(url)
        
        if not video_id:
            st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.")
            return

        st.info("Video ID detected! Processing...")
        
        transcript = None
        
        # Try different transcription methods based on selection
        if transcription_method == "YouTube Built-in":
            # Get available languages
            st.session_state.available_languages = get_available_languages(video_id)
            
            if st.session_state.available_languages:
                # Add language selection
                selected_language = st.selectbox(
                    "Select transcript language:",
                    st.session_state.available_languages,
                    index=0
                )
                
                # Get transcript in selected language
                transcript = get_transcript_in_language(video_id, selected_language)
                
                if transcript:
                    st.success(f"Transcript successfully extracted in {selected_language}!")
            else:
                st.warning("No built-in transcripts available for this video.")
        
        if not transcript and transcription_method != "YouTube Built-in":
            st.warning("Attempting to generate transcript using selected method...")
            
            with st.spinner("Downloading audio and generating transcript (this may take a few minutes)..."):
                # Download audio
                audio_data = download_audio(url, video_id)
                
                if not audio_data:
                    st.error("Failed to download audio. Please try again later.")
                    return

                # Transcribe using selected method
                if transcription_method == "Whisper AI":
                    transcript = transcribe_with_whisper(audio_data)
                else:  # Google Speech Recognition
                    transcript = transcribe_with_speech_recognition(audio_data)
                
                if transcript:
                    st.success(f"Transcript successfully generated using {transcription_method}!")
                else:
                    st.error(f"Failed to generate transcript using {transcription_method}. Please try another method.")
                    return

        if transcript:
            display_transcript(transcript, video_id)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.session_state.error = str(e)
    finally:
        st.session_state.processing = False

def process_audio_file(uploaded_file, transcription_method):
    """Process uploaded audio file for transcription."""
    try:
        st.session_state.processing = True
        st.session_state.error = None

        # Read the uploaded file
        audio_data = uploaded_file.read()

        with st.spinner("Generating transcript (this may take a few minutes)..."):
            # Transcribe using selected method
            if transcription_method == "Whisper AI":
                transcript = transcribe_with_whisper(audio_data)
            else:  # Google Speech Recognition
                transcript = transcribe_with_speech_recognition(audio_data)
            
            if transcript:
                st.success(f"Transcript successfully generated using {transcription_method}!")
                display_transcript(transcript, uploaded_file.name)
            else:
                st.error(f"Failed to generate transcript using {transcription_method}. Please try another method.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.session_state.error = str(e)
    finally:
        st.session_state.processing = False

def display_transcript(transcript, file_id):
    """Display transcript and provide download option."""
    # Display transcript
    st.text_area("Transcript:", transcript, height=400)
    
    # Save transcript to file
    saved_path = save_transcript(transcript, file_id)
    if saved_path:
        st.success(f"Transcript saved to: {saved_path}")
    
    # Add download button
    st.download_button(
        label="Download Transcript",
        data=transcript,
        file_name=f"transcript_{file_id}.txt",
        mime="text/plain"
    )

if __name__ == "__main__":
    main() 