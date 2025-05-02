import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from youtube_transcript_api.proxies import WebshareProxyConfig
from pytube import YouTube
import whisper
import os
import re

# —– إضافة تهيئة بروكسي (اختياري) —–
# proxy_cfg = WebshareProxyConfig(proxy_username="USER", proxy_password="PASS")
# ytt_api = YouTubeTranscriptApi(proxy_config=proxy_cfg)
ytt_api = YouTubeTranscriptApi()

model = whisper.load_model("base")  # تحميل موديل Whisper

def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None

def fallback_whisper(video_url):
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    out_file = audio_stream.download(filename="temp_audio.mp4")
    result = model.transcribe("temp_audio.mp4", language="ar")
    os.remove("temp_audio.mp4")
    # تقسيم إلى فقرات
    text = result["text"]
    return text.replace('. ', '.\n\n').replace('؟ ', '؟\n\n').replace('! ', '!\n\n')

def get_transcript(video_url):
    vid = extract_video_id(video_url)
    if not vid:
        raise ValueError("رابط الفيديو غير صالح.")
    try:
        data = ytt_api.fetch(vid, languages=['ar','en'])
        # دمج النصوص
        text = " ".join([seg["text"] for seg in data])
        return text.replace('. ', '.\n\n').replace('؟ ', '؟\n\n').replace('! ', '!\n\n')
    except NoTranscriptFound:
        # إذا لا توجد ترجمة يوتيوب
        return fallback_whisper(video_url)
    except Exception:
        # أي خطأ آخر (مثل IP Blocked) → اعتماد على Whisper
        return fallback_whisper(video_url)

# —– واجهة Streamlit —–
st.title("استخراج النص من فيديو YouTube مع بروكسي أو Whisper")
url = st.text_input("أدخل رابط الفيديو")
if url:
    with st.spinner("جارٍ المعالجة…"):
        try:
            paragraphs = get_transcript(url)
            st.text_area("النص المستخرج", paragraphs, height=400)
            st.download_button("تحميل .txt", paragraphs, file_name="transcript.txt")
        except Exception as e:
            st.error(str(e))