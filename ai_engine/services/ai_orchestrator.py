import json
from .gemini_service import generate_text
from .prompt_service import build_plan_prompt
from planner.models import Project, Section
from .pubsub import save_ai_history, get_default_publisher

publisher = get_default_publisher()


def run_ai_planning(project: Project):
    publisher.publish(project.id, "planning_started", 10)

    prompt = build_plan_prompt(project.name, project.description)
    response_text, usage = generate_text(prompt)

    try:
        data = json.loads(response_text)
    except Exception:
        data = {"overview": response_text}

    Section.objects.update_or_create(
        project=project,
        title="Overview",
        defaults={"content_json": data, "content": response_text},
    )

    save_ai_history(project, "gemini-flash-lite-latest", prompt, response_text, usage)
    publisher.publish(project.id, "planning_completed", 100)

    return data
