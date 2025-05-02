import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import streamlit as st
from pytube import YouTube
import whisper
import tempfile
import time
import re

st.title("استخراج النصوص من فيديوهات YouTube")

video_url = st.text_input("أدخل رابط الفيديو:")

if st.button("بدء الاستخراج") and video_url:
    try:
        with st.spinner("جاري التحقق من الرابط..."):
            try:
                yt = YouTube(video_url)
                video_stream = yt.streams.filter(only_audio=True).first()
                if video_stream is None:
                    st.error("لم يتم العثور على ملف صوتي مناسب في الفيديو.")
                    st.stop()
            except Exception as e:
                st.error(f"تعذر تحميل الفيديو. تأكد من صحة الرابط.\n\nالخطأ: {e}")
                st.stop()

        with st.spinner("جاري تحميل الصوت..."):
            temp_dir = tempfile.mkdtemp()
            audio_path = os.path.join(temp_dir, "audio.mp4")
            video_stream.download(output_path=temp_dir, filename="audio.mp4")

        with st.spinner("جاري استخراج النص باستخدام Whisper..."):
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            text = result["text"]

        # تقسيم النص إلى فقرات
        sentences = re.split(r'(?<=[.!؟]) +', text)
        paragraphs = [' '.join(sentences[i:i+3]) for i in range(0, len(sentences), 3)]

        st.success("تم استخراج النص بنجاح!")

        full_text = ""
        for i, para in enumerate(paragraphs, 1):
            st.markdown(f"**فقرة {i}:** {para}")
            full_text += f"فقرة {i}:\n{para}\n\n"

        st.download_button("تحميل النص كملف", full_text, file_name="video_transcript.txt")

    except Exception as e:
        st.error(f"حدث خطأ غير متوقع أثناء المعالجة:\n\n{e}")