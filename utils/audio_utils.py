import os
import yt_dlp
import streamlit as st
import ssl
import certifi

def download_audio(url, temp_dir):
    """تحميل الصوت من فيديو يوتيوب"""
    try:
        # تكوين SSL
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
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
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=True)
            except Exception as e:
                st.warning("محاولة تحميل بديلة...")
                # محاولة بديلة مع خيارات مختلفة
                ydl_opts['nocheckcertificate'] = True
                ydl_opts['extract_flat'] = True
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    info_dict = ydl2.extract_info(url, download=True)

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

        if not downloaded_filepath:
            raise Exception("لم يتم العثور على الملف الصوتي بعد التحميل")

        return downloaded_filepath
    except Exception as e:
        raise Exception(f"خطأ في تحميل الصوت: {str(e)}") 