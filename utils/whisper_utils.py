import streamlit as st
import subprocess
import sys
import torch

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

def configure_pytorch():
    """تكوين PyTorch بشكل آمن"""
    try:
        torch.set_num_threads(4)
        torch.set_num_interop_threads(4)
    except Exception as e:
        st.warning("تعذر تكوين PyTorch بشكل كامل. سيتم استخدام الإعدادات الافتراضية.") 