import streamlit as st
import os
import subprocess
import sys
import tempfile
import shutil
import yt_dlp
import validators
import io
from docx import Document
import torch
import numpy as np

# تكوين Streamlit
st.set_page_config(
    page_title="تحويل صوت يوتيوب إلى نص",
    page_icon="🎙️",
    layout="centered"
)

# تكوين PyTorch
torch.set_num_threads(4)
torch.set_num_interop_threads(4)

def setup_environment():
    """تثبيت المكتبات المطلوبة"""
    try:
        import whisper
        if not hasattr(whisper, "load_model"):
            raise ImportError("نسخة whisper غير صالحة")
        return whisper
    except Exception:
        st.warning("جاري تثبيت مكتبة whisper...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "git+https://github.com/openai/whisper.git"])
        import whisper
        return whisper

@st.cache_resource(show_spinner=False)
def load_whisper_model():
    """تحميل نموذج Whisper مع التخزين المؤقت"""
    try:
        whisper = setup_environment()
        model = whisper.load_model("base")
        return model
    except Exception as e:
        st.error(f"خطأ في تحميل النموذج: {str(e)}")
        return None

def download_audio(url, temp_dir):
    """تحميل الصوت من فيديو يوتيوب"""
    try:
        audio_filename_template = os.path.join(temp_dir, 'audio')
        ydl_opts = {
            'format': 'bestaudio/best',
            'extract_audio': True,
            'audio_format': 'wav',
            'outtmpl': audio_filename_template,
            'noplaylist': True,
            'nocheckcertificate': True,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_filepath = None
            
            if 'requested_downloads' in info_dict and info_dict['requested_downloads']:
                downloaded_filepath = info_dict['requested_downloads'][0]['filepath']
            elif 'entries' in info_dict:
                if info_dict['entries'] and 'requested_downloads' in info_dict['entries'][0] and info_dict['entries'][0]['requested_downloads']:
                    downloaded_filepath = info_dict['entries'][0]['requested_downloads'][0]['filepath']
            else:
                for fname in os.listdir(temp_dir):
                    if fname.startswith(os.path.basename(audio_filename_template)):
                        downloaded_filepath = os.path.join(temp_dir, fname)
                        break

        return downloaded_filepath
    except Exception as e:
        raise Exception(f"خطأ في تحميل الصوت: {str(e)}")

def create_download_files(text):
    """إنشاء ملفات التحميل"""
    try:
        # ملف Word
        docx_buffer = io.BytesIO()
        doc = Document()
        doc.add_paragraph(text)
        doc.save(docx_buffer)
        docx_buffer.seek(0)

        # ملف نصي
        txt_buffer = text.encode('utf-8')

        return docx_buffer.getvalue(), txt_buffer
    except Exception as e:
        raise Exception(f"خطأ في إنشاء الملفات: {str(e)}")

def main():
    # العنوان الرئيسي
    st.title("🎙️ تحويل صوت يوتيوب إلى نص")
    
    # شرح بسيط
    st.markdown("""
    <div style='text-align: right; margin-bottom: 20px;'>
        <p>أدخل رابط فيديو يوتيوب وسيقوم التطبيق بتحويل الصوت إلى نص.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # واجهة المستخدم
    youtube_url = st.text_input("رابط فيديو يوتيوب:", placeholder="مثال: https://www.youtube.com/watch?v=...")
    
    if st.button("تحميل وتحويل", type="primary", use_container_width=True):
        if not youtube_url:
            st.warning("الرجاء إدخال رابط فيديو.")
            return

        if not validators.url(youtube_url):
            st.error("الرجاء إدخال رابط يوتيوب صحيح.")
            return

        temp_dir = None
        try:
            # إنشاء مجلد مؤقت
            temp_dir = tempfile.mkdtemp()

            # تحميل الصوت
            with st.spinner("⏳ جاري تحميل الصوت من الفيديو..."):
                downloaded_filepath = download_audio(youtube_url, temp_dir)

            if not downloaded_filepath or not os.path.exists(downloaded_filepath):
                st.error("لم يتم العثور على الملف الصوتي المحمل.")
                return

            st.success("✅ تم تحميل الصوت بنجاح.")

            # تحميل النموذج
            with st.spinner("⏳ جاري تحميل نموذج التحويل..."):
                model = load_whisper_model()
                if model is None:
                    st.error("فشل في تحميل النموذج. يرجى المحاولة مرة أخرى.")
                    return

            # تحويل الصوت إلى نص
            with st.spinner("⏳ جاري تحويل الصوت إلى نص..."):
                try:
                    result = model.transcribe(downloaded_filepath)
                    text = result["text"]
                except Exception as e:
                    st.error(f"خطأ في تحويل الصوت إلى نص: {str(e)}")
                    return

            st.success("✅ تم تحويل الصوت إلى نص!")

            # عرض النص
            st.subheader("النص المستخرج:")
            st.text_area("", text, height=300)

            # إنشاء ملفات التحميل
            try:
                docx_data, txt_data = create_download_files(text)

                # أزرار التحميل
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📄 تحميل كملف Word",
                        data=docx_data,
                        file_name="transcription.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                with col2:
                    st.download_button(
                        label="📝 تحميل كملف نصي",
                        data=txt_data,
                        file_name="transcription.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"خطأ في إنشاء ملفات التحميل: {str(e)}")

        except Exception as e:
            st.error(f"حدث خطأ غير متوقع: {str(e)}")
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    # تذييل الصفحة
    st.markdown("""
    <div style='text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid #eee;'>
        <p style='color: #666;'>تستخدم هذه الأداة:</p>
        <code>streamlit</code> • <code>yt-dlp</code> • <code>whisper</code> • <code>python-docx</code>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()