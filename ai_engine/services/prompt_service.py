prompt_templates = {
    "overview": """
        You are an expert **software project architect**.
        Your task is to write a clear, compelling overview of a software project.

        ## Context
        Project name: {project_name}
        Description (if provided): "{description}"

        ## Instructions
        - Summarize the purpose and vision of the project.
        - Identify the target users and core value proposition.
        - Highlight what makes this project unique or technically interesting.
        - Keep it concise (3–5 paragraphs).
        - Write in **neutral, professional tone** suitable for a project planning document.

        ## Output Format
        Return your answer as **plain Markdown**, no bullet numbers, no metadata.
    """,
    "features": """
        You are an experienced **product manager** and **system analyst**.
        Generate a structured list of key product features for this project.

        ## Context
        Project name: {project_name}
        Related things:
        {context}

        ## Instructions
        - Derive 5–8 meaningful, user-facing features from the overview.
        - Each feature should include:
        - `name`: short descriptive title
        - `description`: 1–2 sentences explaining the functionality
        - `priority`: high / medium / low (based on importance)
        - Avoid implementation details.
        - Be realistic and modular — features should map well to tasks later.

        ## Output Format
        Return JSON and JSON only, no markdown, ... and in this format (no code block markdown like: 
        ```json
        {{
        "frontend": [...],
        "backend": [...]
        }}
        ```):
        {{
        "features": [
            {{ "name": "", "description": "", "priority": "" }}
        ]
        }}
    """,
    "tech_stack": """
        You are a **senior full-stack software architect**.
        Propose the most suitable technology stack for the following project.

        ## Context
        Project name: {project_name}
        Related things:
        {context}

        ## Instructions
        - Recommend **frontend**, **backend**, **database**, **infrastructure**, and **AI/ML tools** (if relevant).
        - Consider scalability, developer experience, and cost.
        - If multiple options fit, explain trade-offs briefly.
        - Prefer **modern, maintainable** technologies used in real projects.
        - Include `justification` explaining *why* each stack element fits the project.

        ## Output Format
        Return JSON and JSON only, no markdown, ... and in this format (no code block markdown like: 
        ```json
        {{
        "frontend": [...],
        "backend": [...]
        }}
        ```):
        {{
        "frontend": [{{ "tech": "", "reason": "" }}],
        "backend": [{{ "tech": "", "reason": "" }}],
        "database": [{{ "tech": "", "reason": "" }}],
        "ai_services": [{{ "tech": "", "reason": "" }}],
        "devops": [{{ "tech": "", "reason": "" }}]
        }}
    """,
    "tasks": """
        You are a **technical project manager** and **Scrum planner**.
        Break down this project into actionable development tasks and milestones.

        ## Context
        Project name: {project_name}
        Related things:
        {context}

        ## Instructions
        - Organize tasks logically under milestones.
        - Each task should include:
        - `title`: concise task name
        - `description`: what needs to be done
        - `role`: suggested assignee (frontend / backend / AI / devops)
        - `priority`: high / medium / low
        - Do not repeat feature names as tasks — instead, **break them down** into implementation steps.
        - Avoid fictional deadlines, just group logically.

        ## Output Format
        Return JSON and JSON only, no markdown, ... and in this format (no code block markdown like: 
        ```json
        {{
        "frontend": [...],
        "backend": [...]
        }}
        ```):
        {{
            "milestones": [
                {{
                "name": "MVP Setup",
                "tasks": [
                    {{ "title": "", "description": "", "role": "", "priority": "" }}
                ]
                }}
            ]
        }}
    """,
    "docs": """
        You are a **technical writer** and **software documentation specialist**.
        Your job is to generate clear, developer-oriented documentation
        based on the project’s context.

        ## Context
        Project name: {project_name}
        Related things:
        {context}

        ## Instructions
        - Generate a well-structured Markdown document containing:
        1. Introduction
        2. System Architecture (high-level)
        3. API Design summary
        4. Deployment & Configuration notes
        5. Future improvements
        - Avoid code — keep it conceptual and explanatory.
        - Write in concise, professional English.

        ## Output Format
        Return the result in **Markdown** format, no extra JSON wrapping.
    """,
}
