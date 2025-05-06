from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import streamlit as st

def get_youtube_transcript(video_id):
    """
    Get transcript from YouTube's built-in transcript system.
    
    Args:
        video_id (str): The YouTube video ID
        
    Returns:
        str: The formatted transcript text if available, None otherwise
    """
    try:
        # Get transcript from YouTube
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format the transcript
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(transcript)
        
        return formatted_transcript
    except Exception as e:
        st.error(f"Error getting YouTube transcript: {str(e)}")
        return None

def get_available_languages(video_id):
    """
    Get list of available transcript languages for the video.
    
    Args:
        video_id (str): The YouTube video ID
        
    Returns:
        list: List of available language codes
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        return [transcript.language_code for transcript in transcript_list]
    except Exception as e:
        st.error(f"Error getting available languages: {str(e)}")
        return []

def get_transcript_in_language(video_id, language_code):
    """
    Get transcript in a specific language.
    
    Args:
        video_id (str): The YouTube video ID
        language_code (str): The language code (e.g., 'en', 'ar', 'fr')
        
    Returns:
        str: The formatted transcript text if available, None otherwise
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        formatter = TextFormatter()
        return formatter.format_transcript(transcript)
    except Exception as e:
        st.error(f"Error getting transcript in {language_code}: {str(e)}")
        return None 