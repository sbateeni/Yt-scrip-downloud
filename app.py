import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

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

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        return formatter.format_transcript(transcript)
    except Exception as e:
        return f"Error: {str(e)}"

# Set page configuration
st.set_page_config(
    page_title="YouTube Transcript Extractor",
    page_icon="🎥",
    layout="centered"
)

# Add title and description
st.title("🎥 YouTube Transcript Extractor")
st.markdown("""
This application extracts transcripts from YouTube videos. 
Simply paste any YouTube video URL below and get the transcript!
""")

# Input field for YouTube URL
url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    video_id = extract_video_id(url)
    
    if video_id:
        st.info("Video ID detected! Fetching transcript...")
        
        transcript = get_transcript(video_id)
        
        if transcript.startswith("Error"):
            st.error(transcript)
        else:
            st.success("Transcript successfully extracted!")
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
st.markdown("Made with ❤️ using Streamlit") 