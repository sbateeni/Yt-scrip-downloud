from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
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
    except TranscriptsDisabled:
        st.error("Subtitles are disabled for this video")
        return None
    except NoTranscriptFound:
        st.error("No transcript found for this video")
        return None
    except Exception as e:
        st.error(f"Error getting transcript: {str(e)}")
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
        # First try to get any transcript to check if subtitles are enabled
        try:
            YouTubeTranscriptApi.get_transcript(video_id)
        except TranscriptsDisabled:
            st.error("Subtitles are disabled for this video")
            return []
        except NoTranscriptFound:
            st.warning("No transcript found for this video")
            return []
            
        # If we get here, subtitles are enabled, so get the list
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        languages = []
        
        # Get manually created transcripts
        try:
            manual_transcripts = transcript_list.find_manually_created_transcript()
            languages.append({
                'code': manual_transcripts.language_code,
                'name': manual_transcripts.language,
                'type': 'Manual'
            })
        except:
            pass
            
        # Get generated transcripts
        try:
            generated_transcripts = transcript_list.find_generated_transcript()
            languages.append({
                'code': generated_transcripts.language_code,
                'name': generated_transcripts.language,
                'type': 'Generated'
            })
        except:
            pass
            
        # Get all available transcripts
        try:
            for transcript in transcript_list:
                if not any(lang['code'] == transcript.language_code for lang in languages):
                    languages.append({
                        'code': transcript.language_code,
                        'name': transcript.language,
                        'type': 'Available'
                    })
        except:
            pass
            
        if not languages:
            st.warning("No built-in transcripts available for this video.")
            return []
            
        return languages
        
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
        formatted_transcript = formatter.format_transcript(transcript)
        return formatted_transcript
    except TranscriptsDisabled:
        st.error(f"Subtitles are disabled for this video in {language_code}")
        return None
    except NoTranscriptFound:
        st.error(f"No transcript found for this video in {language_code}")
        return None
    except Exception as e:
        st.error(f"Error getting transcript in {language_code}: {str(e)}")
        return None 