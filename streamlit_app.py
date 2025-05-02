
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def get_transcript_paragraphs(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return None, "الرابط غير صالح."

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ar', 'en'])
        formatter = TextFormatter()
        text = formatter.format_transcript(transcript)

        # تقسيم النص إلى فقرات حسب علامات الترقيم
        paragraphs = text.replace('. ', '.\n\n').replace('؟ ', '؟\n\n').replace('! ', '!\n\n')

        return paragraphs, None
    except Exception as e:
        return None, f"حدث خطأ: {e}"

# واجهة ستريمليت
st.set_page_config(page_title="استخراج نص من يوتيوب", layout="centered")
st.title("استخراج النصوص من فيديوهات YouTube")

video_url = st.text_input("أدخل رابط الفيديو:")

if video_url:
    with st.spinner("جارٍ استخراج النص..."):
        paragraphs, error = get_transcript_paragraphs(video_url)
    
    if error:
        st.error(error)
    elif paragraphs:
        st.subheader("النص المستخرج:")
        st.text_area("النص على شكل فقرات", value=paragraphs, height=400)

        # حفظ كملف TXT
        st.download_button(
            label="تحميل النص كملف .txt",
            data=paragraphs,
            file_name="youtube_transcript.txt",
            mime="text/plain"
        )
