import os
import yt_dlp
import streamlit as st

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