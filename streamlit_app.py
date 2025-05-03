import streamlit as st
import whisper
import tempfile
import os
import re
import subprocess

st.set_page_config(page_title="استخراج النصوص من YouTube", layout="centered")
st.title("استخراج النصوص من فيديو YouTube")

def clean_youtube_url(url):
    # ينظف الروابط المختصرة أو روابط الجوال
    url = url.replace("m.youtube.com", "www.youtube.com")
    url = re.sub(r"\?si=.*", "", url)
    url = re.sub(r"&.*", "", url)
    return url

video_url = st.text_input("أدخل رابط فيديو YouTube:")

if st.button("استخراج النص"):
    if not video_url:
        st.warning("يرجى إدخال رابط.")
    else:
        try:
            st.info("جاري تحميل الفيديو...")

            # تنظيف الرابط
            cleaned_url = clean_youtube_url(video_url)

            with tempfile.TemporaryDirectory() as tmpdir:
                audio_path = os.path.join(tmpdir, "audio.mp3")

                # تحميل الصوت فقط باستخدام yt-dlp
                cmd = [
                    "yt-dlp",
                    "-f", "bestaudio",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "-o", audio_path,
                    cleaned_url
                ]
                subprocess.run(cmd, check=True)

                st.info("جاري تحويل الصوت إلى نص...")

                model = whisper.load_model("base")
                result = model.transcribe(audio_path, fp16=False)

                text = result["text"].strip()
                paragraphs = text.split(". ")
                formatted_text = "\n\n".join(p.strip() for p in paragraphs if p)

                st.success("تم استخراج النص بنجاح!")
                st.text_area("النص المستخرج:", value=formatted_text, height=300)
                st.download_button("تحميل النص كملف .txt", formatted_text, file_name="transcript.txt")

        except subprocess.CalledProcessError:
            st.error("فشل تحميل الفيديو. تأكد من أن الرابط صحيح.")
        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")