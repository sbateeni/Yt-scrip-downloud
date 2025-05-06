import yt_dlp
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
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'no_color': True,
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash', 'hls'],
                        'player_client': ['android'],
                        'player_skip': ['js', 'configs', 'webpage']
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise Exception("Could not extract video information")
                
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'length': info.get('duration', 0),
                    'author': info.get('uploader', 'Unknown Author'),
                    'views': info.get('view_count', 0)
                }
                
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
                continue
            st.error(f"Error getting video info: {str(e)}")
            return None
    return None

def download_youtube_audio(url, max_retries=3):
    """Download YouTube video audio with improved error handling and retry mechanism"""
    for attempt in range(max_retries):
        try:
            if not is_valid_youtube_url(url):
                st.error("Invalid YouTube URL format")
                return None

            # Create a temporary file with .mp3 extension
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': temp_file.name,
                    'quiet': True,
                    'no_warnings': True,
                    'nocheckcertificate': True,
                    'ignoreerrors': True,
                    'no_color': True,
                    'extractor_args': {
                        'youtube': {
                            'skip': ['dash', 'hls'],
                            'player_client': ['android'],
                            'player_skip': ['js', 'configs', 'webpage']
                        }
                    },
                    'format_sort': ['acodec:mp4a.40.2'],
                    'prefer_ffmpeg': True,
                    'keepvideo': False,
                    'writethumbnail': False,
                    'verbose': True,
                    'postprocessor_args': [
                        '-ar', '44100',  # Set audio sample rate
                        '-ac', '2',      # Set audio channels to stereo
                        '-b:a', '192k'   # Set audio bitrate
                    ]
                }

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    
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

    # Download with progress
    with st.spinner("Downloading video..."):
        audio_path = download_youtube_audio(url)
        
    if audio_path:
        st.success("Download completed successfully!")
        return audio_path
    return None 