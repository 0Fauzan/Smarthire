from utils.text_extractor import extract_resume_text


def parse_resume(filepath):
    raw_text = extract_resume_text(filepath)

    # Clean text (basic)
    cleaned_text = " ".join(raw_text.split())

    return {
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        "word_count": len(cleaned_text.split())
    }
