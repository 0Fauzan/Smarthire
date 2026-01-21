import os
from pdfminer.high_level import extract_text
from docx import Document


def extract_text_from_pdf(path):
    return extract_text(path)


def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_resume_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext in [".doc", ".docx"]:
        return extract_text_from_docx(filepath)
    else:
        raise ValueError("Unsupported file format")
