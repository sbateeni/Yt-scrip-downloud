import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
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
        # First try to get the transcript in the original language
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return format_transcript(transcript_list)
    except (TranscriptsDisabled, NoTranscriptFound):
        try:
            # If original language fails, try to get available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get English transcript first
            try:
                transcript = transcript_list.find_transcript(['en'])
                return format_transcript(transcript.fetch())
            except:
                # If English is not available, get the first available transcript
                transcript = transcript_list.find_generated_transcript(['en', 'ar', 'fr', 'es', 'de'])
                return format_transcript(transcript.fetch())
        except Exception as e:
            return f"Error: Could not retrieve transcript. {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

def format_transcript(transcript_list):
    formatted_transcript = ""
    for entry in transcript_list:
        formatted_transcript += entry['text'] + " "
    return formatted_transcript.strip()

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