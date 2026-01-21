import os
import requests

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}


def hf_generate_questions(prompt, count=4):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.8
        }
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)

    if response.status_code != 200:
        raise Exception("HF API failed")

    text = response.json()[0]["generated_text"]

    questions = [
        q.strip("- ").strip()
        for q in text.split("\n")
        if "?" in q
    ]

    return questions[:count]
