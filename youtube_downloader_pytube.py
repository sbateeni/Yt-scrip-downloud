from pytube import YouTube
import streamlit as st
import tempfile
import os
import re
import time

def is_valid_youtube_url(url):
    """Validate YouTube URL format"""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    return bool(re.match(youtube_regex, url))

def get_video_info(url, max_retries=3):
    """Get video information with retry mechanism"""
    for attempt in range(max_retries):
        try:
            yt = YouTube(url)
            return {
                'title': yt.title,
                'length': yt.length,
                'author': yt.author,
                'views': yt.views,
                'captions': yt.captions
            }
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
                continue
            st.error(f"Error getting video info: {str(e)}")
            return None
    return None

def get_youtube_captions(url, max_retries=3):
    """Get captions from YouTube video"""
    for attempt in range(max_retries):
        try:
            yt = YouTube(url)
            captions = yt.captions
            
            if not captions:
                return None
                
            # Try to get English captions first
            caption = captions.get_by_language_code('en')
            if not caption:
                # If no English captions, get the first available language
                caption = list(captions.values())[0]
            
            # Get the caption text
            caption_text = caption.generate_srt_captions()
            return caption_text
            
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
                continue
            st.error(f"Error getting captions: {str(e)}")
            return None
    return None

def download_youtube_audio(url, max_retries=3):
    """Download YouTube video audio with improved error handling and retry mechanism"""
    for attempt in range(max_retries):
        try:
            if not is_valid_youtube_url(url):
                st.error("Invalid YouTube URL format")
                return None

            # Create YouTube object
            yt = YouTube(url)
            
            # Get audio stream
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            if not audio_stream:
                st.error("No audio stream found")
                return None

            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                try:
                    # Download the audio
                    audio_stream.download(filename=temp_file.name)
                    
                    # Verify the file exists and has content
                    if os.path.exists(temp_file.name) and os.path.getsize(temp_file.name) > 0:
                        return temp_file.name
                    else:
                        raise Exception("Downloaded file is empty or does not exist")
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        st.warning(f"Download attempt {attempt + 1} failed, retrying...")
                        time.sleep(2)
                        continue
                    st.error(f"Download Error: {str(e)}")
                    return None

        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
                continue
            st.error(f"Error processing video: {str(e)}")
            return None
    return None

def cleanup_temp_file(file_path):
    """Clean up temporary file"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        st.warning(f"Error cleaning up temporary file: {str(e)}")

def download_video_with_progress(url):
    """Download video with progress bar and improved error handling"""
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

    # Try to get captions first
    captions = get_youtube_captions(url)
    if captions:
        st.success("Found YouTube captions!")
        return None, captions

    # If no captions, download audio for transcription
    with st.spinner("Downloading video..."):
        audio_path = download_youtube_audio(url)
        
    if audio_path:
        st.success("Download completed successfully!")
        return audio_path, None
    return None, None 