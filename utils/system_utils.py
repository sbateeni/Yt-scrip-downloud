import os
import sys
import platform
import subprocess
import streamlit as st
import tempfile
import shutil
import requests
import zipfile
import tarfile
from pathlib import Path

def get_ffmpeg_url():
    """Get the appropriate FFmpeg download URL based on the operating system."""
    system = platform.system().lower()
    if system == "windows":
        return "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    elif system == "linux":
        return "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    else:
        raise Exception(f"Unsupported operating system: {system}")

def download_file(url, output_path):
    """Download a file from URL to the specified path."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        st.error(f"Error downloading file: {str(e)}")
        return False

def extract_ffmpeg(archive_path, extract_dir):
    """Extract FFmpeg from the downloaded archive."""
    try:
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif archive_path.endswith('.tar.xz'):
            with tarfile.open(archive_path, 'r:xz') as tar_ref:
                tar_ref.extractall(extract_dir)
        return True
    except Exception as e:
        st.error(f"Error extracting FFmpeg: {str(e)}")
        return False

def setup_ffmpeg():
    """Download and setup FFmpeg."""
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Get FFmpeg URL
            ffmpeg_url = get_ffmpeg_url()
            
            # Download FFmpeg
            archive_path = os.path.join(temp_dir, "ffmpeg_archive")
            if not download_file(ffmpeg_url, archive_path):
                return False
            
            # Extract FFmpeg
            if not extract_ffmpeg(archive_path, temp_dir):
                return False
            
            # Find FFmpeg executable
            ffmpeg_exe = None
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.lower() in ['ffmpeg.exe', 'ffmpeg']:
                        ffmpeg_exe = os.path.join(root, file)
                        break
                if ffmpeg_exe:
                    break
            
            if not ffmpeg_exe:
                st.error("Could not find FFmpeg executable in the downloaded files")
                return False
            
            # Create FFmpeg directory in user's home
            ffmpeg_dir = os.path.join(str(Path.home()), '.ffmpeg')
            os.makedirs(ffmpeg_dir, exist_ok=True)
            
            # Copy FFmpeg to the FFmpeg directory
            target_path = os.path.join(ffmpeg_dir, os.path.basename(ffmpeg_exe))
            shutil.copy2(ffmpeg_exe, target_path)
            
            # Add FFmpeg directory to PATH
            os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']
            
            return True
            
    except Exception as e:
        st.error(f"Error setting up FFmpeg: {str(e)}")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True)
        return result.returncode == 0
    except:
        return False

def install_requirements():
    """Install required Python packages."""
    try:
        # Install required packages
        packages = [
            'openai-whisper==20231117',
            'torch==2.2.0',
            'SpeechRecognition==3.10.1',
            'pydub==0.25.1',
            'ffmpeg-python==0.2.0'
        ]
        
        for package in packages:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        
        return True
    except Exception as e:
        st.error(f"Error installing requirements: {str(e)}")
        return False

def verify_installation():
    """Verify that all required components are installed and working."""
    try:
        # Check Python packages
        import whisper
        import torch
        import speech_recognition
        import pydub
        
        # Check FFmpeg
        if not check_ffmpeg():
            st.error("""
            FFmpeg is not installed. Please add FFmpeg to your Streamlit Cloud app:
            1. Go to your app's settings in Streamlit Cloud
            2. Add the following to the 'Packages' section:
               ffmpeg
            3. Deploy your app again
            """)
            return False
        
        return True
    except ImportError as e:
        st.warning(f"Missing required package: {str(e)}. Installing...")
        return install_requirements()
    except Exception as e:
        st.error(f"Error verifying installation: {str(e)}")
        return False 