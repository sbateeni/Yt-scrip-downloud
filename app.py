import streamlit as st
from faster_whisper import WhisperModel
import os
from youtube_downloader import download_video_with_progress, cleanup_temp_file

# Set page configuration
st.set_page_config(
    page_title="YouTube Video Transcription",
    page_icon="🎥",
    layout="wide"
)

# Title and description
st.title("🎥 YouTube Video Transcription")
st.markdown("""
This application transcribes YouTube videos using Faster Whisper.
The process is:
1. Download video from YouTube
2. Convert to MP3 audio
3. Extract text using Whisper AI
""")

# Initialize Whisper model
@st.cache_resource
def load_whisper_model():
    # Use the base model for better performance
    return WhisperModel("base", device="cpu", compute_type="int8")

# Function to transcribe audio
def transcribe_audio(audio_path):
    try:
        model = load_whisper_model()
        st.info("Starting transcription process...")
        
        # Transcribe the audio file
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        # Combine all segments into one text
        full_text = " ".join([segment.text for segment in segments])
        
        st.success("Transcription completed!")
        return full_text
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

# Main application
def main():
    # Input for YouTube URL
    youtube_url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("Transcribe"):
        if youtube_url:
            # Step 1: Download video and convert to MP3
            with st.spinner("Step 1/2: Downloading video and converting to MP3..."):
                audio_path = download_video_with_progress(youtube_url)
                
            if audio_path:
                # Step 2: Transcribe the audio
                with st.spinner("Step 2/2: Transcribing audio..."):
                    transcription = transcribe_audio(audio_path)
                    
                if transcription:
                    st.success("Transcription completed!")
                    st.text_area("Transcription:", transcription, height=300)
                    
                # Clean up temporary file
                cleanup_temp_file(audio_path)
        else:
            st.warning("Please enter a YouTube URL")

if __name__ == "__main__":
    main() 