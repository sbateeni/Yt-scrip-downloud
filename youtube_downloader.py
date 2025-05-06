from pytube import YouTube
import streamlit as st
import tempfile
import os
from urllib.error import HTTPError
import re

def is_valid_youtube_url(url):
    """Validate YouTube URL format"""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    return bool(re.match(youtube_regex, url))

def get_video_info(url):
    """Get video information"""
    try:
        yt = YouTube(url)
        return {
            'title': yt.title,
            'length': yt.length,
            'author': yt.author,
            'views': yt.views
        }
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
        return None

def download_youtube_audio(url):
    """Download YouTube video audio with improved error handling"""
    try:
        if not is_valid_youtube_url(url):
            st.error("Invalid YouTube URL format")
            return None

        # Create YouTube object with custom options
        yt = YouTube(
            url,
            use_oauth=False,
            allow_oauth_cache=True
        )

        # Get available streams
        audio_streams = yt.streams.filter(only_audio=True)
        
        if not audio_streams:
            st.error("No audio streams found for this video")
            return None

        # Select the best audio stream (highest bitrate)
        audio_stream = audio_streams.order_by('abr').desc().first()

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            try:
                # Download with progress
                audio_stream.download(filename=temp_file.name)
                return temp_file.name
            except HTTPError as e:
                st.error(f"HTTP Error: {str(e)}")
                return None
            except Exception as e:
                st.error(f"Download Error: {str(e)}")
                return None

    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        return None

def cleanup_temp_file(file_path):
    """Clean up temporary file"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        st.warning(f"Error cleaning up temporary file: {str(e)}")

# Example usage in Streamlit
def download_video_with_progress(url):
    """Download video with progress bar"""
    if not url:
        st.warning("Please enter a YouTube URL")
        return None

    # Show video information
    video_info = get_video_info(url)
    if video_info:
        st.info(f"""
        Title: {video_info['title']}
        Author: {video_info['author']}
        Length: {video_info['length']} seconds
        Views: {video_info['views']:,}
        """)

    # Download with progress
    with st.spinner("Downloading video..."):
        audio_path = download_youtube_audio(url)
        
    if audio_path:
        st.success("Download completed successfully!")
        return audio_path
    return None 