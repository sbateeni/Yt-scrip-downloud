import os
import yt_dlp
import streamlit as st
import ssl
import certifi
import urllib3
import requests
import subprocess
import sys

def download_audio(url, temp_dir):
    """تحميل الصوت من فيديو يوتيوب"""
    try:
        # تكوين SSL
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        urllib3.disable_warnings()
        
        # تحديث yt-dlp
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
        except Exception as e:
            st.warning("تعذر تحديث yt-dlp، سيتم استخدام الإصدار الحالي")
        
        audio_filename_template = os.path.join(temp_dir, 'audio')
        ydl_opts = {
            'format': 'bestaudio/best',
            'extract_audio': True,
            'audio_format': 'wav',
            'outtmpl': audio_filename_template,
            'noplaylist': True,
            'nocheckcertificate': True,
            'logtostderr': False,
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': 30,
            'extractor_args': {
                'youtube': {
                    'skip_download_archive': True,
                    'player_client': ['android', 'web'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'source_address': '0.0.0.0',
            'geo_bypass': True,
            'geo_verification_proxy': None,
            'extract_flat': False,
            'ignoreerrors': True,
            'no_color': True,
            'prefer_insecure': True,
            'http_chunk_size': 10485760,
            'ssl_verify': False,
        }

        # محاولة التحميل المباشر
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                st.info("جاري تحميل الفيديو...")
                # أولاً، الحصول على معلومات الفيديو
                info = ydl.extract_info(url, download=False)
                st.info(f"تم العثور على الفيديو: {info.get('title', 'بدون عنوان')}")
                
                # ثم تحميل الصوت
                info_dict = ydl.extract_info(url, download=True)
                st.info("تم تحميل الفيديو بنجاح")
        except Exception as e:
            st.warning(f"محاولة تحميل بديلة... (الخطأ: {str(e)})")
            # محاولة بديلة مع خيارات مختلفة
            ydl_opts.update({
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'nocheckcertificate': True,
                'extract_flat': True,
                'prefer_insecure': True,
                'geo_bypass': True,
                'geo_verification_proxy': None,
                'source_address': '0.0.0.0',
                'ssl_verify': False,
            })
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    st.info("جاري تحميل الفيديو (المحاولة الثانية)...")
                    info = ydl2.extract_info(url, download=False)
                    st.info(f"تم العثور على الفيديو: {info.get('title', 'بدون عنوان')}")
                    info_dict = ydl2.extract_info(url, download=True)
                    st.info("تم تحميل الفيديو بنجاح")
            except Exception as e2:
                st.warning(f"محاولة تحميل نهائية... (الخطأ: {str(e2)})")
                # محاولة نهائية مع خيارات أبسط
                ydl_opts.update({
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'extract_audio': True,
                    'audio_format': 'wav',
                    'nocheckcertificate': True,
                    'prefer_insecure': True,
                    'geo_bypass': True,
                    'extract_flat': True,
                    'ssl_verify': False,
                })
                with yt_dlp.YoutubeDL(ydl_opts) as ydl3:
                    st.info("جاري تحميل الفيديو (المحاولة النهائية)...")
                    info = ydl3.extract_info(url, download=False)
                    st.info(f"تم العثور على الفيديو: {info.get('title', 'بدون عنوان')}")
                    info_dict = ydl3.extract_info(url, download=True)
                    st.info("تم تحميل الفيديو بنجاح")

        # البحث عن الملف المحمل
        st.info("جاري البحث عن الملف الصوتي...")
        downloaded_filepath = None
        
        # عرض محتويات المجلد المؤقت
        st.info(f"محتويات المجلد المؤقت: {os.listdir(temp_dir)}")
        
        # البحث عن الملف بامتدادات مختلفة
        for ext in ['.wav', '.mp3', '.m4a', '.webm']:
            for fname in os.listdir(temp_dir):
                if fname.startswith(os.path.basename(audio_filename_template)) or fname.endswith(ext):
                    downloaded_filepath = os.path.join(temp_dir, fname)
                    st.success(f"تم العثور على الملف: {fname}")
                    break
            if downloaded_filepath:
                break

        if not downloaded_filepath:
            raise Exception("لم يتم العثور على الملف الصوتي بعد التحميل")

        # التحقق من وجود الملف وحجمه
        if os.path.exists(downloaded_filepath):
            file_size = os.path.getsize(downloaded_filepath)
            st.info(f"حجم الملف: {file_size / 1024 / 1024:.2f} MB")
            if file_size == 0:
                raise Exception("الملف المحمل فارغ")
        else:
            raise Exception(f"الملف غير موجود: {downloaded_filepath}")

        return downloaded_filepath
    except Exception as e:
        raise Exception(f"خطأ في تحميل الصوت: {str(e)}") 