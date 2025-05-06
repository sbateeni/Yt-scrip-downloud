import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

st.set_page_config(page_title="YouTube Transcript Downloader", page_icon="🎥")

st.title("YouTube Transcript Downloader")
st.write("Enter a YouTube video URL to get its transcript")

def extract_video_id(url):
    # Regular expression to match YouTube video IDs
    pattern = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # Format the transcript into a readable text
        formatted_transcript = ""
        for entry in transcript_list:
            formatted_transcript += entry['text'] + " "
        return formatted_transcript.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Input for YouTube URL
youtube_url = st.text_input("Enter YouTube Video URL")

if youtube_url:
    video_id = extract_video_id(youtube_url)
    
    if video_id:
        st.write("Video ID:", video_id)
        
        if st.button("Get Transcript"):
            with st.spinner("Fetching transcript..."):
                transcript = get_transcript(video_id)
                
                if transcript.startswith("Error"):
                    st.error(transcript)
                else:
                    st.text_area("Transcript", transcript, height=400)
                    
                    # Download button
                    st.download_button(
                        label="Download Transcript",
                        data=transcript,
                        file_name=f"transcript_{video_id}.txt",
                        mime="text/plain"
                    )
    else:
        st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.") 