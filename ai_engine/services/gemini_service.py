import os, time, json, hashlib
import google.generativeai as genai
from django.conf import settings
from planner.models import Project, Section
from .cost_tracker import record_ai_usage

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()


def generate_text(prompt: str, model_name="gemini-flash-lite-latest", temperature=0.7):
    """Send prompt to Gemini and return structured response"""
    start = time.time()
    model = genai.GenerativeModel(model_name)

    response = model.generate_content(prompt)
    duration = int((time.time() - start) * 1000)

    text = response.text if hasattr(response, "text") else str(response)
    usage = {
        "input": response.prompt_feedback or {},
        "output_tokens": getattr(response, "usage_metadata", {}),
        "duration_ms": duration,
    }

    return text, usage
