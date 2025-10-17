from ..services.gemini_service import generate_text
from .context_manager import load_context, save_section
from ..services.prompt_service import prompt_templates


def _project_attr(project, attr, default=""):
    if isinstance(project, dict):
        return project.get(attr) or default
    return getattr(project, attr, default)


def generate_overview(project):
    project_id = _project_attr(project, "id")
    project_name = _project_attr(project, "name")
    description = _project_attr(project, "description") or "No description provided."
    prompt = prompt_templates["overview"].format(
        project_name=project_name,
        description=description,
    )

    text = generate_text(project_id=project_id, step="overview", prompt=prompt)
    save_section(project, "Overview", text, 1)
    return text


def generate_tech_stack(project):
    context = load_context(project)
    project_name = _project_attr(project, "name")
    project_id = _project_attr(project, "id")
    prompt = prompt_templates["tech_stack"].format(
        project_name=project_name, context=context
    )

    text = generate_text(project_id=project_id, step="techstack", prompt=prompt)
    save_section(project, "Tech Stack", text, 2)
    return text


def generate_features(project):
    context = load_context(project)
    project_name = _project_attr(project, "name")
    project_id = _project_attr(project, "id")
    prompt = prompt_templates["features"].format(
        project_name=project_name, context=context
    )

    text = generate_text(project_id=project_id, step="features", prompt=prompt)
    save_section(project, "Features", text, 3)
    return text


def generate_tasks(project):
    context = load_context(project)
    project_name = _project_attr(project, "name")
    project_id = _project_attr(project, "id")
    prompt = prompt_templates["tasks"].format(
        project_name=project_name, context=context
    )

    text = generate_text(project_id=project_id, step="tasks", prompt=prompt)
    save_section(project, "Tasks", text, 3)
    return text


def generate_docs(project):
    context = load_context(project)
    project_name = _project_attr(project, "name")
    project_id = _project_attr(project, "id")
    prompt = prompt_templates["docs"].format(project_name=project_name, context=context)

    text = generate_text(project_id=project_id, step="docs", prompt=prompt)
    save_section(project, "Docs", text, 3)
    return text
