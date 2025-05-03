import streamlit as st
import yt_dlp
import whisper
import os
import tempfile
import shutil
import validators # للحقق من الرابط بشكل أفضل

# عنوان التطبيق
st.title("أداة تحويل صوت فيديو يوتيوب إلى نص")

# إدخال رابط الفيديو من المستخدم
youtube_url = st.text_input("الرجاء إدخال رابط فيديو يوتيوب:")

# زر بدء العملية
if st.button("تحميل الصوت وتحويله إلى نص"):
    if youtube_url:
        # التحقق من صحة الرابط بشكل مبدئي
        if not validators.url(youtube_url):
            st.error("الرجاء إدخال رابط يوتيوب صحيح.")
        else:
            temp_dir = None  # تهيئة متغير المسار المؤقت
            try:
                # استخدام مجلد مؤقت لتخزين الملفات بشكل آمن وسهل الحذف
                temp_dir = tempfile.mkdtemp()
                audio_filename_template = os.path.join(temp_dir, 'audio') # yt-dlp سيضيف الامتداد

                st.info("جاري تحميل الصوت من الفيديو...")
                with st.spinner("الرجاء الانتظار..."):
                    ydl_opts = {
                        'format': 'bestaudio/best',  # اختيار أفضل جودة صوت
                        'extract_audio': True,       # استخراج الصوت فقط
                        'audio_format': 'wav',       # تحويل الصوت إلى صيغة WAV (متوافقة جيدًا مع Whisper)
                        'outtmpl': audio_filename_template, # مسار واسم الملف المؤقت
                        'noplaylist': True,          # عدم معالجة قوائم التشغيل إذا كان الرابط جزءاً منها
                        'nocheckcertificate': True,  # لتجنب مشاكل شهادات SSL
                        'logtostderr': False,        # عدم عرض سجلات yt-dlp على الخطأ القياسي
                        'quiet': True,               # تقليل إخراج yt-dlp
                        'no_warnings': True,         # إخفاء التحذيرات
                    }

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(youtube_url, download=True)
                        # yt-dlp يرجع معلومات عن الملف المحمل، بما في ذلك المسار الفعلي
                        downloaded_filepath = None
                        if 'requested_downloads' in info_dict and info_dict['requested_downloads']:
                             downloaded_filepath = info_dict['requested_downloads'][0]['filepath']
                        elif 'entries' in info_dict: # التعامل مع قوائم التشغيل (قد يحدث حتى مع noplaylist=True)
                            if info_dict['entries'] and 'requested_downloads' in info_dict['entries'][0] and info_dict['entries'][0]['requested_downloads']:
                                 downloaded_filepath = info_dict['entries'][0]['requested_downloads'][0]['filepath']
                        else: # محاولة تخمين المسار كحل بديل
                            # yt-dlp يضيف الامتداد (مثل .wav) إلى outtmpl
                            # يمكننا محاولة البحث عن الملف الذي يبدأ بـ outtmpl في المجلد المؤقت
                            for fname in os.listdir(temp_dir):
                                if fname.startswith(os.path.basename(audio_filename_template)):
                                    downloaded_filepath = os.path.join(temp_dir, fname)
                                    break


                if downloaded_filepath and os.path.exists(downloaded_filepath):
                    st.success("تم تحميل الصوت بنجاح.")

                    st.info("جاري تحميل نموذج تحويل الكلام إلى نص (قد يستغرق بعض الوقت أول مرة)...")
                    with st.spinner("الرجاء الانتظار..."):
                        # استخدام st.cache_resource لتحميل النموذج مرة واحدة فقط
                        # 'base' هو نموذج صغير وسريع ومناسب لمعظم اللغات
                        # يمكنك استخدام 'small', 'medium', 'large' للحصول على دقة أعلى على حساب السرعة وحجم الذاكرة
                        @st.cache_resource
                        def load_whisper_model(model_name):
                            return whisper.load_model(model_name)

                        # قم بتغيير 'base' إلى نموذج آخر إذا لزم الأمر
                        model = load_whisper_model("base")

                    st.info("جاري تحويل الصوت إلى نص...")
                    with st.spinner("الرجاء الانتظار..."):
                        # تحويل الصوت إلى نص باستخدام نموذج Whisper
                        # الدالة transcribe ترجع قاموسًا يحتوي على النص المستخرج
                        transcription_result = model.transcribe(downloaded_filepath)
                        transcribed_text = transcription_result["text"]

                    st.success("تم تحويل الصوت إلى نص بنجاح!")

                    st.subheader("النص المستخرج:")
                    # عرض النص في مربع نص قابل للتمرير
                    st.text_area("نص الفيديو", transcribed_text, height=400)

                else:
                    st.error("حدث خطأ في العثور على ملف الصوت المحمل.")


            except yt_dlp.utils.DownloadError as e:
                st.error(f"خطأ في تحميل الفيديو: {e}")
            except Exception as e:
                st.error(f"حدث خطأ غير متوقع: {e}")
                st.error(f"تفاصيل الخطأ: {e}") # عرض تفاصيل الخطأ للمساعدة في التتبع
            finally:
                # التأكد من حذف المجلد المؤقت وملفاته في النهاية
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    #st.info("تم تنظيف الملفات المؤقتة.") # يمكن تفعيل هذا السطر للعرض

    else:
        st.warning("الرجاء إدخال رابط فيديو يوتيوب للمتابعة.")

# معلومات إضافية
st.markdown("""
<br>
<p style='text-align: center;'>
تستخدم هذه الأداة المكتبات التالية:
<br>
<code>streamlit</code> لإنشاء الواجهة الرسومية.
<br>
<code>yt-dlp</code> لتحميل الصوت من فيديو يوتيوب.
<br>
<code>whisper</code> لتحويل الصوت إلى نص.
</p>
""", unsafe_allow_html=True)

