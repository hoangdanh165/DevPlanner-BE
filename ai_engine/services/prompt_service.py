prompt_templates = {
    "overview": """
        You are an expert **software project architect**.
        Your task is to write a clear, compelling overview of a software project.

        ## Context
        Project name: $project_name
        Description (if provided): $description

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
        Project name: $project_name
        Related things:
        $context

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
        {
        "frontend": [...],
        "backend": [...]
        }
        ```):
        {
        "features": [
            { "name": "", "description": "", "priority": "" }
        ]
        }
    """,
    "tech_stack": """
        You are a **senior full-stack software architect**.
        Propose the most suitable technology stack for the following project.

        ## Context
        Project name: $project_name
        Related things:
        $context

        ## Instructions
        - Recommend **frontend**, **backend**, **database**, **infrastructure**, and **AI/ML tools** (if relevant).
        - Consider scalability, developer experience, and cost.
        - If multiple options fit, explain trade-offs briefly.
        - Prefer **modern, maintainable** technologies used in real projects.
        - Include `justification` explaining *why* each stack element fits the project.

        ## Output Format
        Return JSON and JSON only, no markdown, ... and in this format (no code block markdown like: 
        ```json
        {
        "frontend": [...],
        "backend": [...]
        }
        ```):
        {
        "frontend": [{ "tech": "", "reason": "" }],
        "backend": [{ "tech": "", "reason": "" }],
        "database": [{ "tech": "", "reason": "" }],
        "ai_services": [{ "tech": "", "reason": "" }],
        "devops": [{ "tech": "", "reason": "" }]
        }
    """,
    "tasks": """
        You are a **technical project manager** and **Scrum planner**.
        Break down this project into actionable development tasks and milestones.

        ## Context
        Project name: $project_name
        Related things:
        $context

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
        {
        "frontend": [...],
        "backend": [...]
        }
        ```):
        {
            "milestones": [
                {
                "name": "MVP Setup",
                "tasks": [
                    { "title": "", "description": "", "role": "", "priority": "" }
                ]
                }
            ]
        }
    """,
    "docs": """
        You are a **technical writer** and **software documentation specialist**.
        Your job is to generate clear, developer-oriented documentation
        based on the project’s context.

        ## Context
        Project name: $project_name
        Related things:
        $context

        ## Instructions
        - Generate a well-structured Markdown document containing:
        1. Introduction
        2. System Architecture (high-level)
        3. API Design summary
        4. Deployment & Configuration notes
        5. Future improvements
        6. References — include real, authoritative technical documents, articles, or papers related to the technologies used.
            - Group the references by **tech category** (e.g., Frontend, Backend, Database, DevOps, AI, etc.).
            - Under each category, list 2–5 relevant resources.
            - Format each reference as: **[Title](URL)** — Author(s) or Organization, short description if needed.
            - Example:
            - **Frontend**
                - **[React Documentation](https://react.dev)** — Official guide by Meta.
                - **[Next.js Deployment Guide](https://nextjs.org/docs/deployment)** — Official Next.js documentation for production deployment.
            - **Backend**
                - **[Django REST Framework](https://www.django-rest-framework.org/)** — Official API development guide.
        - Avoid code — keep it conceptual and explanatory.
        - Write in concise, professional English.

        ## Output Format
        Return the result in **Markdown** format, no extra JSON wrapping.
    """,
    "diagrams": {
        "gantt_chart": """
        You are a **project planner** and **timeline visualizer**.

        Your task is to generate a **Mermaid Gantt chart** that visualizes the high-level schedule and dependencies of the project.

        ## Context
        Project name: $project_name
        Related things:
        $context

        ## Requirements
        - Use Mermaid v11.x syntax!!
        - Use realistic phases like: Planning, Design, Development, Testing, Deployment.
        - Include estimated durations and sequential dependencies.
        - Group tasks logically (Frontend, Backend, AI, Infrastructure, etc.)
        - Use proper Mermaid Gantt syntax with realistic time spacing.
        - The first line must start with `gantt` and include `title`, `dateFormat`, and `section` definitions.
        - Do not include Markdown code fences or ```mermaid tags.

        ## Output Format
        Return **only** the raw Mermaid Gantt code, nothing else (no explanations, no Markdown fences).

        Example Output:
        gantt
            title A Gantt Diagram
            dateFormat  YYYY-MM-DD
            section Section
            A task           :a1, 2014-01-01, 30d
            Another task     :after a1  , 20d
            section Another
            Task in sec      :2014-01-12  , 12d
            another task      : 24d
    """,
        "er_diagram": """
        You are a **database architect**.

        Your task is to generate a **Mermaid Entity Relationship Diagram (ERD)** that clearly represents the data model of the project.

        ## Context
        Project name: $project_name
        Related things:
        $context

        ## Requirements
        - Use Mermaid v11.x syntax!!
        - Use `erDiagram` syntax.
        - Include entities (tables) with key attributes and relationships.
        - Represent One-to-Many (||--o{), Many-to-Many ({--}), and One-to-One (||--||) correctly.
        - Base the relationships logically on the project context.
        - Do not include Markdown code fences or ```mermaid tags.

        ## Output Format
        Return **only** the raw Mermaid ERD code, nothing else.

        Example Output:
        erDiagram
            USER ||--o{ PROJECT : "creates"
            PROJECT ||--o{ SECTION : "contains"
            SECTION ||--o{ TASK : "includes"
    """,
        "architecture_diagram": """
        You are a **software architect**.

        Your task is to generate a **high-level system architecture diagram** using Mermaid syntax.

        ## Context
        Project name: $project_name
        Related things:
        $context

        ## Requirements
        - Use Mermaid v11.x syntax!!
        - Use `architecture-beta` syntax.
        - Show how the main components interact: frontend, backend, database, AI services, external APIs, message brokers, etc.
        - Keep it simple, readable, and logically grouped.
        - Do not include Markdown code fences or ```mermaid tags.

        ## Output Format
        Return **only** the raw Mermaid graph code, nothing else.

        Example Output:
        architecture-beta
            group api(cloud)[API]

            service db(database)[Database] in api
            service disk1(disk)[Storage] in api
            service disk2(disk)[Storage] in api
            service server(server)[Server] in api

            db:L -- R:server
            disk1:T -- B:server
            disk2:T -- B:db
    """,
        "sequence_diagram": """
        You are a **software engineer** visualizing the main user flow.

        Your task is to generate a **Mermaid sequence diagram** that shows the core interaction steps between key components of the system.

        ## Context
        Project name: $project_name
        Related things:
        $context

        ## Requirements
        - Use Mermaid v11.x syntax!!
        - Use `sequenceDiagram` syntax.
        - Show the main interaction from user action to backend logic and AI response.
        - Include key participants (User, Frontend, Backend, Database, Celery/Worker, AI API, WebSocket/Realtime server).
        - Keep message names short and meaningful.
        - Do not include Markdown code fences or ```mermaid tags.

        ## Output Format
        Return **only** the raw Mermaid sequence diagram code, nothing else.

        Example Output:
        sequenceDiagram
            Alice->>+John: Hello John, how are you?
            Alice->>+John: John, can you hear me?
            John-->>-Alice: Hi Alice, I can hear you!
            John-->>-Alice: I feel great!
    """,
    },
}
