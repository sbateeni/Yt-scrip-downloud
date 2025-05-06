import os
import yt_dlp
import streamlit as st
import ssl
import certifi
import urllib3
import requests

def download_audio(url, temp_dir):
    """تحميل الصوت من فيديو يوتيوب"""
    try:
        # تكوين SSL
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        urllib3.disable_warnings()
        
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
        }

        # محاولة التحميل المباشر
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
        except Exception as e:
            st.warning("محاولة تحميل بديلة...")
            # محاولة بديلة مع خيارات مختلفة
            ydl_opts.update({
                'nocheckcertificate': True,
                'extract_flat': True,
                'prefer_insecure': True,
                'geo_bypass': True,
                'geo_verification_proxy': None,
                'source_address': '0.0.0.0',
            })
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    info_dict = ydl2.extract_info(url, download=True)
            except Exception as e2:
                st.warning("محاولة تحميل نهائية...")
                # محاولة نهائية مع خيارات أبسط
                ydl_opts.update({
                    'format': 'bestaudio',
                    'extract_audio': True,
                    'audio_format': 'wav',
                    'nocheckcertificate': True,
                    'prefer_insecure': True,
                    'geo_bypass': True,
                    'extract_flat': True,
                })
                with yt_dlp.YoutubeDL(ydl_opts) as ydl3:
                    info_dict = ydl3.extract_info(url, download=True)

        downloaded_filepath = None
        
        # البحث عن الملف المحمل
        for fname in os.listdir(temp_dir):
            if fname.startswith(os.path.basename(audio_filename_template)):
                downloaded_filepath = os.path.join(temp_dir, fname)
                break

        if not downloaded_filepath:
            raise Exception("لم يتم العثور على الملف الصوتي بعد التحميل")

        return downloaded_filepath
    except Exception as e:
        raise Exception(f"خطأ في تحميل الصوت: {str(e)}") 