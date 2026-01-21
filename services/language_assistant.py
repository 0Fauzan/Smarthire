import os
import requests
from services.rule_language_fallback import rule_based_language_help

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}


def ai_language_assist(text, source_language="auto"):
    prompt = f"""
Improve the following interview answer for professional English.
If the input is not English, translate it to professional English.

Text:
{text}

Rules:
- Keep meaning same
- Improve confidence and clarity
- Do not add new information
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.6
        }
    }

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=20
        )

        if response.status_code != 200:
            raise Exception("HF API failed")

        output = response.json()[0]["generated_text"]

        return {
            "original": text,
            "suggested": output.strip(),
            "tips": [
                "Maintain eye contact while speaking",
                "Pause briefly instead of using filler words"
            ],
            "communication_score": 80
        }

    except Exception:
        # 🔒 Guaranteed fallback
        return rule_based_language_help(text)
