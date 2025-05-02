import streamlit as st
from pytube import YouTube
import whisper
import os
import tempfile
import re

st.set_page_config(page_title="استخراج النصوص من YouTube", layout="centered")
st.title("استخراج النصوص من فيديو YouTube")

def extract_video_id(url):
    regex = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
    match = re.search(regex, url)
    return match.group(1) if match else None

video_url = st.text_input("أدخل رابط فيديو YouTube:")

if st.button("استخراج النص"):
    if not video_url:
        st.warning("الرجاء إدخال رابط.")
    else:
        try:
            # تنظيف الرابط
            clean_url = re.sub(r"&.*|\\?si=.*", "", video_url).replace("m.youtube.com", "www.youtube.com")

            video_id = extract_video_id(clean_url)
            if not video_id:
                st.error("تعذر استخراج معرف الفيديو. تحقق من الرابط.")
            else:
                st.info("جاري تحميل الفيديو...")

                yt = YouTube(clean_url)
                audio_stream = yt.streams.filter(only_audio=True).first()

                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_audio:
                    audio_path = tmp_audio.name
                    audio_stream.download(filename=audio_path)

                st.info("جاري تحويل الصوت إلى نص...")

                model = whisper.load_model("base")
                result = model.transcribe(audio_path, fp16=False)

                text = result["text"].strip()
                paragraphs = text.split(". ")
                formatted_text = "\n\n".join(p.strip() for p in paragraphs if p)

                st.success("تم استخراج النص بنجاح!")
                st.text_area("النص المستخرج:", value=formatted_text, height=300)
                st.download_button("تحميل النص كملف .txt", formatted_text, file_name="transcript.txt")

                os.remove(audio_path)

        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")