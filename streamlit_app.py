import streamlit as st
import yt_dlp
import os
import tempfile
import shutil
import validators  # للتحقق من الرابط
import importlib

# التحقق من مكتبة Whisper الصحيحة
try:
    whisper = importlib.import_module("whisper")
    if not hasattr(whisper, "load_model"):
        raise ImportError("Whisper المثبتة ليست من OpenAI. يرجى تثبيت النسخة الرسمية.")
except ImportError as e:
    st.error(f"خطأ في تحميل مكتبة Whisper: {e}")
    st.stop()

# عنوان التطبيق
st.title("أداة تحويل صوت فيديو يوتيوب إلى نص")

# إدخال رابط الفيديو من المستخدم
youtube_url = st.text_input("الرجاء إدخال رابط فيديو يوتيوب:")

# زر بدء العملية
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

                    st.info("جاري تحميل نموذج تحويل الكلام إلى نص...")
                    with st.spinner("الرجاء الانتظار..."):
                        @st.cache_resource
                        def load_whisper_model(model_name):
                            return whisper.load_model(model_name)

                        model = load_whisper_model("base")

                    st.info("جاري تحويل الصوت إلى نص...")
                    with st.spinner("الرجاء الانتظار..."):
                        transcription_result = model.transcribe(downloaded_filepath)
                        transcribed_text = transcription_result["text"]

                    st.success("تم تحويل الصوت إلى نص بنجاح!")
                    st.subheader("النص المستخرج:")
                    st.text_area("نص الفيديو", transcribed_text, height=400)

                else:
                    st.error("حدث خطأ في العثور على ملف الصوت المحمل.")

            except yt_dlp.utils.DownloadError as e:
                st.error(f"خطأ في تحميل الفيديو: {e}")
            except Exception as e:
                st.error("حدث خطأ غير متوقع أثناء التنفيذ.")
                st.error(f"تفاصيل الخطأ: {e}")
            finally:
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
    else:
        st.warning("الرجاء إدخال رابط فيديو يوتيوب للمتابعة.")

# معلومات إضافية
st.markdown("""
<br>
<p style='text-align: center;'>
تستخدم هذه الأداة المكتبات التالية:
<br>
<code>streamlit</code> لإنشاء الواجهة الرسومية.<br>
<code>yt-dlp</code> لتحميل الصوت من فيديو يوتيوب.<br>
<code>whisper</code> لتحويل الصوت إلى نص.<br>
</p>
""", unsafe_allow_html=True)