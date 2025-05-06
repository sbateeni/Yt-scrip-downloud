import streamlit as st
import os
import tempfile
import shutil
import validators

from utils.whisper_utils import configure_pytorch, load_whisper_model
from utils.audio_utils import download_audio
from utils.file_utils import create_download_files

# تكوين Streamlit
st.set_page_config(
    page_title="تحويل صوت يوتيوب إلى نص",
    page_icon="🎙️",
    layout="centered"
)

# تكوين PyTorch
configure_pytorch()

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