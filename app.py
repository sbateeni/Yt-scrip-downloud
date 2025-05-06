import streamlit as st
import validators
from utils.youtube_utils import clean_youtube_url, extract_video_id, is_video_available, download_audio
from utils.youtube_transcript import get_youtube_transcript, get_available_languages, get_transcript_in_language
from utils.transcript_utils import transcribe_with_whisper, transcribe_with_google, save_transcript
from utils.system_utils import verify_installation
import tempfile
import os

# Initialize session state variables
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

def main():
    st.title("🎥 YouTube Video Transcript Extractor")
    st.markdown("""
    This application helps you extract transcripts from YouTube videos using different methods:
    1. YouTube's built-in transcripts (if available)
    2. Whisper AI (OpenAI's speech recognition)
    3. Google Speech Recognition
    
    You can also upload your own audio file for transcription.
    """)
    
    # Verify installation
    if not verify_installation():
        st.error("Please wait while we install the required components...")
        return
        
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["YouTube Video", "Audio File"])
    
    with tab1:
        st.header("YouTube Video")
        url = st.text_input("Enter YouTube URL:")
        
        if url:
            if not validators.url(url):
                st.error("Please enter a valid URL")
                return
                
            video_id = extract_video_id(url)
            if not video_id:
                st.error("Could not extract video ID from URL")
                return
                
            if not is_video_available(url):
                st.error("Video is not available or is restricted")
                return
                
            # Get available languages
            st.session_state.available_languages = get_available_languages(video_id)
            
            if st.session_state.available_languages:
                st.success(f"Found {len(st.session_state.available_languages)} available transcript(s)")
                
                # Create language selection
                language_options = {f"{lang['name']} ({lang['type']})": lang['code'] 
                                  for lang in st.session_state.available_languages}
                selected_language = st.selectbox(
                    "Select transcript language:",
                    options=list(language_options.keys())
                )
                
                if st.button("Get Transcript"):
                    st.session_state.processing = True
                    try:
                        # Get transcript in selected language
                        transcript = get_transcript_in_language(
                            video_id,
                            language_options[selected_language]
                        )
                        
                        if transcript:
                            display_transcript(transcript, "YouTube Transcript")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                    finally:
                        st.session_state.processing = False
            else:
                st.warning("No built-in transcripts available. Please try another method.")
            
            # Show other transcription methods
            st.subheader("Alternative Transcription Methods")
            method = st.radio(
                "Select transcription method:",
                ["Whisper AI", "Google Speech Recognition"]
            )
            
            if st.button("Transcribe"):
                st.session_state.processing = True
                try:
                    # Download audio
                    audio_data = download_audio(url, video_id)
                    if not audio_data:
                        st.error("Failed to download audio")
                        return
                        
                    # Save audio to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                        temp_file.write(audio_data)
                        temp_file_path = temp_file.name
                        
                    try:
                        if method == "Whisper AI":
                            transcript = transcribe_with_whisper(temp_file_path)
                        else:
                            transcript = transcribe_with_google(temp_file_path)
                            
                        if transcript:
                            display_transcript(transcript, f"{method} Transcript")
                            
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_file_path):
                            os.unlink(temp_file_path)
                            
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    st.session_state.processing = False
    
    with tab2:
        st.header("Audio File")
        uploaded_file = st.file_uploader(
            "Upload an audio file",
            type=['mp3', 'wav', 'm4a', 'ogg']
        )
        
        if uploaded_file:
            method = st.radio(
                "Select transcription method:",
                ["Whisper AI", "Google Speech Recognition"]
            )
            
            if st.button("Transcribe Audio"):
                st.session_state.processing = True
                try:
                    # Save uploaded file to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_file.name.split(".")[-1]}') as temp_file:
                        temp_file.write(uploaded_file.getvalue())
                        temp_file_path = temp_file.name
                        
                    try:
                        if method == "Whisper AI":
                            transcript = transcribe_with_whisper(temp_file_path)
                        else:
                            transcript = transcribe_with_google(temp_file_path)
                            
                        if transcript:
                            display_transcript(transcript, f"{method} Transcript")
                            
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_file_path):
                            os.unlink(temp_file_path)
                            
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    st.session_state.processing = False

def display_transcript(transcript, title):
    """Display transcript with download option."""
    st.subheader(title)
    st.text_area("Transcript:", transcript, height=300)
    
    # Add download button
    st.download_button(
        label="Download Transcript",
        data=transcript,
        file_name="transcript.txt",
        mime="text/plain"
    )

if __name__ == "__main__":
    main() 