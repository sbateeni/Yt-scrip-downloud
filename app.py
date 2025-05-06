import streamlit as st
import whisper
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
This application transcribes YouTube videos using Whisper AI.
Simply paste a YouTube URL and get the transcription!
""")

# Initialize Whisper model
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

# Function to transcribe audio
def transcribe_audio(audio_path):
    try:
        model = load_whisper_model()
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

# Main application
def main():
    # Input for YouTube URL
    youtube_url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("Transcribe"):
        if youtube_url:
            # Download video using the new downloader
            audio_path = download_video_with_progress(youtube_url)
                
            if audio_path:
                with st.spinner("Transcribing audio..."):
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