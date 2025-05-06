import streamlit as st
from youtube_downloader_pytube import download_video_with_progress, cleanup_temp_file
from faster_whisper import WhisperModel
import os

# Set page config
st.set_page_config(
    page_title="YouTube Video Transcriber",
    page_icon="🎥",
    layout="wide"
)

# Title and description
st.title("🎥 YouTube Video Transcriber")
st.markdown("""
This application allows you to:
1. Get captions directly from YouTube if available
2. If no captions are available, download audio and transcribe it using AI
3. Get accurate transcriptions in multiple languages

**How it works:**
1. Enter a YouTube URL
2. The app will first try to get captions directly from YouTube
3. If no captions are available, it will download the video and transcribe it using Whisper AI
4. You'll get the full transcription with timestamps

**Note:** The transcription process might take a few minutes depending on the video length.
""")

# Initialize session state
if 'transcription' not in st.session_state:
    st.session_state.transcription = None

# Input for YouTube URL
url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    # Try to get captions or download video
    audio_path, captions = download_video_with_progress(url)
    
    if captions:
        # Display YouTube captions
        st.subheader("YouTube Captions:")
        
        # Add options for displaying captions
        display_option = st.radio(
            "Choose display format:",
            ["Formatted (with timestamps)", "Plain text"]
        )
        
        if display_option == "Formatted (with timestamps)":
            st.text_area("Captions:", captions, height=400)
        else:
            # Convert SRT to plain text
            plain_text = "\n".join([line for line in captions.split("\n") if not line.strip().isdigit() and "-->" not in line])
            st.text_area("Captions:", plain_text, height=400)
        
        # Add download buttons
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download SRT Format",
                data=captions,
                file_name="captions.srt",
                mime="text/plain"
            )
        with col2:
            st.download_button(
                label="Download Plain Text",
                data=plain_text,
                file_name="captions.txt",
                mime="text/plain"
            )
    
    elif audio_path:
        try:
            # Initialize Whisper model
            with st.spinner("Loading Whisper model..."):
                model = WhisperModel("base", device="cpu", compute_type="int8")
            
            # Transcribe audio
            with st.spinner("Transcribing audio..."):
                segments, info = model.transcribe(audio_path)
                
                # Store transcription in session state
                st.session_state.transcription = list(segments)
                
                # Display language info
                st.info(f"Detected language: {info.language} (confidence: {info.language_probability:.2f})")
            
            # Display transcription
            st.subheader("Transcription:")
            for segment in st.session_state.transcription:
                st.write(f"[{segment.start:.1f}s -> {segment.end:.1f}s] {segment.text}")
            
            # Add download button for transcription
            if st.session_state.transcription:
                transcription_text = "\n".join([f"[{s.start:.1f}s -> {s.end:.1f}s] {s.text}" for s in st.session_state.transcription])
                st.download_button(
                    label="Download Transcription",
                    data=transcription_text,
                    file_name="transcription.txt",
                    mime="text/plain"
                )
        
        except Exception as e:
            st.error(f"Error during transcription: {str(e)}")
        
        finally:
            # Clean up temporary file
            cleanup_temp_file(audio_path)

# Add footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Whisper AI") 