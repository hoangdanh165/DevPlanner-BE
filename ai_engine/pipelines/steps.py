from ..services.gemini_service import generate_text
from .context_manager import load_context, save_section
from ..services.prompt_service import prompt_templates
from string import Template
import logging

logger = logging.getLogger(__name__)


def _get_project_attr(project, attr, default=""):
    if isinstance(project, dict):
        return project.get(attr) or default
    return getattr(project, attr, default)


# ================== OVERVIEW ==================
def generate_overview(project):
    project_id = _get_project_attr(project, "id")
    project_name = _get_project_attr(project, "name")
    description = (
        _get_project_attr(project, "description") or "No description provided."
    )

    prompt_template = Template(prompt_templates["overview"])
    prompt = prompt_template.substitute(
        project_name=project_name, description=description
    )

    text = generate_text(project_id=project_id, step="overview", prompt=prompt)
    save_section(project, "Overview", text, 1)
    return text


# ================== FEATURES ==================
def generate_features(project):
    context = load_context(project)
    project_name = _get_project_attr(project, "name")
    project_id = _get_project_attr(project, "id")

    prompt_template = Template(prompt_templates["features"])
    prompt = prompt_template.substitute(project_name=project_name, context=context)

    text = generate_text(project_id=project_id, step="features", prompt=prompt)
    save_section(project, "Features", text, 3)
    return text


# ================== TECHSTACK ==================
def generate_tech_stack(project):
    context = load_context(project)
    project_name = _get_project_attr(project, "name")
    project_id = _get_project_attr(project, "id")

    prompt_template = Template(prompt_templates["tech_stack"])
    prompt = prompt_template.substitute(project_name=project_name, context=context)

    text = generate_text(project_id=project_id, step="techstack", prompt=prompt)
    save_section(project, "Tech Stack", text, 2)
    return text


# ================== TASKS ==================
def generate_tasks(project):
    context = load_context(project)
    project_name = _get_project_attr(project, "name")
    project_id = _get_project_attr(project, "id")

    prompt_template = Template(prompt_templates["tasks"])
    prompt = prompt_template.substitute(project_name=project_name, context=context)

    text = generate_text(project_id=project_id, step="tasks", prompt=prompt)
    save_section(project, "Tasks", text, 4)
    return text


# ================== DIAGRAMS ==================
def generate_diagrams_gantt(project):
    context = load_context(project)
    project_name = _get_project_attr(project, "name")
    project_id = _get_project_attr(project, "id")

    prompt_template = Template(prompt_templates["diagrams"]["gantt_chart"])
    prompt = prompt_template.substitute(project_name=project_name, context=context)

    text = generate_text(project_id=project_id, step="diagrams_gantt", prompt=prompt)
    logger.info(text)
    save_section(project, "GANTT Chart", text, 5)
    return text


def generate_diagrams_er(project):
    context = load_context(project)
    project_name = _get_project_attr(project, "name")
    project_id = _get_project_attr(project, "id")

    prompt_template = Template(prompt_templates["diagrams"]["er_diagram"])
    prompt = prompt_template.substitute(project_name=project_name, context=context)

    text = generate_text(project_id=project_id, step="diagrams_er", prompt=prompt)
    save_section(project, "Entity Relationships Diagram", text, 6)
    return text


def generate_diagrams_architecture(project):
    context = load_context(project)
    project_name = _get_project_attr(project, "name")
    project_id = _get_project_attr(project, "id")

    prompt_template = Template(prompt_templates["diagrams"]["architecture_diagram"])
    prompt = prompt_template.substitute(project_name=project_name, context=context)

    text = generate_text(
        project_id=project_id, step="diagrams_architecture", prompt=prompt
    )
    logger.error(text)
    save_section(project, "Architecture Diagram", text, 7)
    return text


def generate_diagrams_sequence(project):
    context = load_context(project)
    project_name = _get_project_attr(project, "name")
    project_id = _get_project_attr(project, "id")

    prompt_template = Template(prompt_templates["diagrams"]["sequence_diagram"])
    prompt = prompt_template.substitute(project_name=project_name, context=context)

    text = generate_text(project_id=project_id, step="diagrams_sequence", prompt=prompt)
    save_section(project, "Sequence Diagram", text, 8)
    return text


# ================== DOCS ==================
def generate_docs(project):
    context = load_context(project)
    project_name = _get_project_attr(project, "name")
    project_id = _get_project_attr(project, "id")

    prompt_template = Template(prompt_templates["docs"])
    prompt = prompt_template.substitute(project_name=project_name, context=context)

    text = generate_text(project_id=project_id, step="docs", prompt=prompt)

    save_section(project, "Docs", text, 9)
    return text
