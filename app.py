import streamlit as st
import validators
import sys
import os

# Import utility functions
from utils.youtube_utils import extract_video_id, download_audio, is_video_available
from utils.youtube_transcript import get_youtube_transcript, get_available_languages, get_transcript_in_language
from utils.transcript_utils import (
    transcribe_with_whisper,
    transcribe_with_speech_recognition,
    save_transcript
)
from utils.system_utils import check_ffmpeg, install_requirements

def initialize_session_state():
    """Initialize session state variables."""
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'error' not in st.session_state:
        st.session_state.error = None
    if 'available_languages' not in st.session_state:
        st.session_state.available_languages = []

def main():
    # Initialize session state
    initialize_session_state()

    # Set page configuration
    st.set_page_config(
        page_title="YouTube Transcript Extractor",
        page_icon="🎥",
        layout="centered"
    )

    # Add title and description
    st.title("🎥 YouTube Transcript Extractor")
    st.markdown("""
    This application extracts transcripts from YouTube videos using multiple methods:
    1. YouTube's built-in transcripts (if available)
    2. AI-powered speech recognition (Whisper)
    3. Google Speech Recognition
    """)

    # Check and install requirements if needed
    if not check_ffmpeg():
        st.warning("FFmpeg is not installed. Installing required components...")
        if install_requirements():
            st.success("Requirements installed successfully!")
        else:
            st.error("Failed to install requirements. Please install FFmpeg manually.")

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
                    audio_path = download_audio(url, video_id)
                    
                    if not audio_path:
                        st.error("Failed to download audio. Please try again later.")
                        return

                    # Transcribe using selected method
                    if transcription_method == "Whisper AI":
                        transcript = transcribe_with_whisper(audio_path)
                    else:  # Google Speech Recognition
                        transcript = transcribe_with_speech_recognition(audio_path)
                    
                    if transcript:
                        st.success(f"Transcript successfully generated using {transcription_method}!")
                    else:
                        st.error(f"Failed to generate transcript using {transcription_method}. Please try another method.")
                        return

            if transcript:
                # Display transcript
                st.text_area("Transcript:", transcript, height=400)
                
                # Save transcript to file
                saved_path = save_transcript(transcript, video_id)
                if saved_path:
                    st.success(f"Transcript saved to: {saved_path}")
                
                # Add download button
                st.download_button(
                    label="Download Transcript",
                    data=transcript,
                    file_name=f"transcript_{video_id}.txt",
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.session_state.error = str(e)
        finally:
            st.session_state.processing = False

    # Add footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit and various transcription tools")

if __name__ == "__main__":
    main() 