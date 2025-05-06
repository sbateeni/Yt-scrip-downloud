import io
from docx import Document

def create_download_files(text):
    """إنشاء ملفات التحميل"""
    try:
        # ملف Word
        docx_buffer = io.BytesIO()
        doc = Document()
        doc.add_paragraph(text)
        doc.save(docx_buffer)
        docx_buffer.seek(0)

        # ملف نصي
        txt_buffer = text.encode('utf-8')

        return docx_buffer.getvalue(), txt_buffer
    except Exception as e:
        raise Exception(f"خطأ في إنشاء الملفات: {str(e)}") 