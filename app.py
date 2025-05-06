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
1. Download audio from any YouTube video
2. Transcribe the audio to text using AI
3. Get accurate transcriptions in multiple languages

**How it works:**
1. Enter a YouTube URL
2. The video will be downloaded and converted to audio
3. The audio will be transcribed using Whisper AI
4. You'll get the full transcription with timestamps

**Note:** The transcription process might take a few minutes depending on the video length.
""")

# Initialize session state
if 'transcription' not in st.session_state:
    st.session_state.transcription = None

# Input for YouTube URL
url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    # Download video
    audio_path = download_video_with_progress(url)
    
    if audio_path:
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