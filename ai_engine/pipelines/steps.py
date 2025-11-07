from ..services.gemini_service import generate_text
from .context_manager import load_context, save_section
from ..services.prompt_service import prompt_templates, build_prompt
from string import Template
import logging

logger = logging.getLogger(__name__)


def _get_project_attr(project, attr, default=""):
    if isinstance(project, dict):
        return project.get(attr) or default
    return getattr(project, attr, default)


# overview, features, tech_stack, tasks, docs, diagrams (gantt, er, sequence, architecture)
def generate(project, section: str, order_index: int) -> str:
    project_id = _get_project_attr(project, "id")
    prompt = build_prompt(project, section)

    step = "diagrams_" + section if "diagrams" in section else section

    text = generate_text(
        project_id=project_id,
        step=step,
        prompt=prompt,
    )

    version = save_section(
        project=project,
        title=section.capitalize(),
        content=text,
        order=order_index,
    )

    return text, version
