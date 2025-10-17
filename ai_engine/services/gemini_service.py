import os, time, json, hashlib
import google.generativeai as genai
from django.conf import settings
from planner.models import Project, Section
from .cost_tracker import record_ai_usage
from .pubsub import get_default_publisher

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

publisher = get_default_publisher()


def hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()


def generate_text(
    project_id: str,
    step: str,
    prompt: str,
    model_name="gemini-flash-lite-latest",
    temperature=0.7,
):
    """Send prompt to Gemini and return structured response"""
    start = time.time()
    model = genai.GenerativeModel(model_name)

    publisher.publish(project_id, f"{step}_start", None)

    stream = model.generate_content(
        prompt,
        stream=True,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
        ),
    )

    full_text = ""
    try:
        for chunk in stream:
            if not chunk.candidates:
                continue
            parts = chunk.candidates[0].content.parts
            if not parts:
                continue
            token = getattr(parts[0], "text", "")
            if not token:
                continue

            full_text += token
            publisher.publish(
                project_id,
                "stream_chunk",
                {"step": step, "text": token},
            )
    except Exception as e:
        publisher.publish(project_id, "stream_error", {"step": step, "error": str(e)})
        raise e

    duration = int((time.time() - start) * 1000)

    publisher.publish(
        project_id,
        f"{step}_end",
        {"total_length": len(full_text), "duration_ms": duration},
    )

    return full_text
