import streamlit as st
import validators
import sys
import os

# Import utility functions
from utils.youtube_utils import extract_video_id, download_audio, is_video_available
from utils.transcript_utils import get_youtube_transcript, transcribe_with_whisper
from utils.system_utils import check_ffmpeg, install_requirements

def initialize_session_state():
    """Initialize session state variables."""
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'error' not in st.session_state:
        st.session_state.error = None

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
    This application extracts transcripts from YouTube videos using two methods:
    1. YouTube's built-in transcripts (if available)
    2. AI-powered speech recognition (Whisper) as a fallback
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
                    
                    if not audio_path:
                        st.error("Failed to download audio. Please try again later.")
                        return

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
                        st.error("Failed to generate transcript. Please try again later.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.session_state.error = str(e)
        finally:
            st.session_state.processing = False

    # Add footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit and Whisper")

if __name__ == "__main__":
    main() 