import streamlit as st
import whisper
from pytube import YouTube
import tempfile
import os

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

# Function to download YouTube video
def download_youtube_audio(url):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            audio_stream.download(filename=temp_file.name)
            return temp_file.name
    except Exception as e:
        st.error(f"Error downloading video: {str(e)}")
        return None

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
            with st.spinner("Downloading video..."):
                audio_path = download_youtube_audio(youtube_url)
                
            if audio_path:
                with st.spinner("Transcribing audio..."):
                    transcription = transcribe_audio(audio_path)
                    
                if transcription:
                    st.success("Transcription completed!")
                    st.text_area("Transcription:", transcription, height=300)
                    
                # Clean up temporary file
                os.unlink(audio_path)
        else:
            st.warning("Please enter a YouTube URL")

if __name__ == "__main__":
    main() 