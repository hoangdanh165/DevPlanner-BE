from ..services.gemini_service import generate_text
from .context_manager import load_context, save_section
from ..services.prompt_service import prompt_templates


def _project_attr(project, attr, default=""):
    if isinstance(project, dict):
        return project.get(attr) or default
    return getattr(project, attr, default)


def generate_overview(project):
    project_name = _project_attr(project, "name")
    description = _project_attr(project, "description") or "No description provided."
    prompt = prompt_templates["overview"].format(
        project_name=project_name,
        description=description,
    )
    print(
        "==================================== OVERVIEW PROMPT ===========================",
        "/n",
        prompt,
    )
    text, usage = generate_text(prompt)
    save_section(project, "Overview", text, 1)
    return text


def generate_tech_stack(project):
    context = load_context(project)
    project_name = _project_attr(project, "name")
    prompt = prompt_templates["tech_stack"].format(
        project_name=project_name, context=context
    )
    print(
        "==================================== TECHSTACK PROMPT ===========================",
        "/n",
        prompt,
    )
    text, usage = generate_text(prompt)
    save_section(project, "Tech Stack", text, 2)
    return text


def generate_features(project):
    context = load_context(project)
    project_name = _project_attr(project, "name")
    prompt = prompt_templates["features"].format(
        project_name=project_name, context=context
    )
    print(
        "==================================== FEATURES PROMPT ===========================",
        "/n",
        prompt,
    )
    text, usage = generate_text(prompt)
    save_section(project, "Features", text, 3)
    return text
