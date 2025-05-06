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

# Set environment variables for PyTorch
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Initialize PyTorch with CPU settings
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cpu":
    torch.set_num_threads(4)

# التأكد من تثبيت whisper
def ensure_whisper_installed():
    try:
        import whisper
        if not hasattr(whisper, "load_model"):
            raise ImportError("نسخة whisper غير صالحة")
        return whisper
    except Exception:
        st.warning("جاري تثبيت مكتبة whisper الرسمية من OpenAI...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "git+https://github.com/openai/whisper.git"])
        import whisper
        return whisper

# Load Whisper model with caching
@st.cache_resource(show_spinner=False)
def load_whisper_model():
    whisper = ensure_whisper_installed()
    return whisper.load_model("base")

st.title("أداة تحويل صوت فيديو يوتيوب إلى نص")
youtube_url = st.text_input("الرجاء إدخال رابط فيديو يوتيوب:")

if st.button("تحميل الصوت وتحويله إلى نص"):
    if youtube_url:
        if not validators.url(youtube_url):
            st.error("الرجاء إدخال رابط يوتيوب صحيح.")
        else:
            temp_dir = None
            try:
                temp_dir = tempfile.mkdtemp()
                audio_filename_template = os.path.join(temp_dir, 'audio')

                st.info("جاري تحميل الصوت من الفيديو...")
                with st.spinner("الرجاء الانتظار..."):
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
                        info_dict = ydl.extract_info(youtube_url, download=True)
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

                if downloaded_filepath and os.path.exists(downloaded_filepath):
                    st.success("تم تحميل الصوت بنجاح.")

                    st.info("جاري تحميل نموذج Whisper...")
                    with st.spinner("الرجاء الانتظار..."):
                        model = load_whisper_model()

                    st.info("جاري تحويل الصوت إلى نص...")
                    with st.spinner("الرجاء الانتظار..."):
                        result = model.transcribe(downloaded_filepath)
                        text = result["text"]

                    st.success("تم تحويل الصوت إلى نص!")
                    st.subheader("النص المستخرج:")
                    st.text_area("نص الفيديو", text, height=400)

                    # تحميل كملف Word
                    docx_buffer = io.BytesIO()
                    doc = Document()
                    doc.add_paragraph(text)
                    doc.save(docx_buffer)
                    docx_buffer.seek(0)

                    st.download_button(
                        label="تحميل كملف Word",
                        data=docx_buffer,
                        file_name="transcription.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                    # تحميل كملف نصي
                    txt_buffer = io.StringIO(text)
                    st.download_button(
                        label="تحميل كملف نصي",
                        data=txt_buffer,
                        file_name="transcription.txt",
                        mime="text/plain"
                    )

                else:
                    st.error("لم يتم العثور على الملف الصوتي المحمل.")
            except yt_dlp.utils.DownloadError as e:
                st.error(f"خطأ في تحميل الفيديو: {e}")
            except Exception as e:
                st.error("حدث خطأ غير متوقع.")
                st.error(f"تفاصيل الخطأ: {e}")
            finally:
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
    else:
        st.warning("الرجاء إدخال رابط فيديو.")

st.markdown("""
<p style='text-align: center;'>
تستخدم هذه الأداة:
<br><code>streamlit</code> • <code>yt-dlp</code> • <code>whisper</code> • <code>python-docx</code>
</p>
""", unsafe_allow_html=True)

# تثبيت python-docx إن لم تكن مثبتة (لبيئة Streamlit Cloud)
try:
    import docx
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])