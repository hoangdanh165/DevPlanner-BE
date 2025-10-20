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
            Project: {project_name}
            Related things:
            {context}

            ## Requirements
            - Use realistic phases like: Planning, Design, Development, Testing, Deployment.
            - Include estimated durations and sequential dependencies.
            - Group tasks logically (Frontend, Backend, AI, Infrastructure, etc.)
            - Use proper Mermaid Gantt syntax with realistic time spacing.

            ## Output Format
            Return **only** the Mermaid code block — nothing else.

            Example Output:
            ```mermaid
            gantt
                title Project Development Timeline
                dateFormat  YYYY-MM-DD
                section Frontend
                UI Design           :a1, 2025-01-01, 5d
                Integration          :a2, after a1, 7d
                section Backend
                API Development      :b1, 2025-01-03, 10d
                Auth System          :b2, after b1, 5d
        """,
        "er_diagram": """
            You are a **database architect**.

            Your task is to generate a **Mermaid Entity Relationship Diagram (ERD)** that clearly represents the data model of the project.

            ## Context
            Project: {project_name}
            Related things:
            {context}

            ## Requirements
            - Use `erDiagram` syntax.
            - Include entities (tables) with key attributes and relationships.
            - Represent One-to-Many (||--o{), Many-to-Many ({--}), and One-to-One (||--||) correctly.
            - Base the relationships logically on the context (e.g., Project → Section → Task).

            ## Output Format
            Return **only** the Mermaid code block — nothing else.

            Example Output:
            ```mermaid
            erDiagram
                USER ||--o{ PROJECT : "creates"
                PROJECT ||--o{ SECTION : "contains"
                SECTION ||--o{ TASK : "includes"
        """,
        "architecture_diagram": """
            You are a **software architect**.

            Your task is to generate a **high-level system architecture diagram** in Mermaid syntax.

            ## Context
            Project: {project_name}
            Tech Stack: {tech_stack}
            Components: {components}
            Description: {description}

            ## Requirements
            - Use `graph TD` syntax.
            - Show how the main components interact: frontend, backend, database, AI services, external APIs, message brokers, etc.
            - Include arrows to represent data flow or communication direction.
            - Keep it simple, readable, and logically grouped.

            ## Output Format
            Return **only** the Mermaid code block — nothing else.

            Example Output:
            ```mermaid
            graph TD
            A[User Interface (Next.js)] --> B[Django REST API]
            B --> C[PostgreSQL Database]
            B --> D[Redis + Celery]
            D --> E[Gemini/OpenAI API]
            E --> B
            B --> A
        """,
        "sequence_diagram": """
            You are a **software engineer** visualizing the main user flow.

            Your task is to generate a **Mermaid sequence diagram** that shows the core interaction steps between key components of the system.

            ## Context
            Project: {project_name}
            Main Flow: {flow_description}
            Tech Stack: {tech_stack}

            ## Requirements
            - Use `sequenceDiagram` syntax.
            - Show the main interaction from user action to backend logic and AI response.
            - Include key participants (User, Frontend, Backend, Database, Celery/Worker, AI API, WebSocket/Realtime server).
            - Keep message names short and meaningful.

            ## Output Format
            Return **only** the Mermaid code block — nothing else.

            Example Output:
            ```mermaid
            sequenceDiagram
            participant U as User
            participant F as Frontend (Next.js)
            participant B as Backend (Django API)
            participant C as Celery Worker
            participant A as AI Service (Gemini/OpenAI)
            participant W as WebSocket Server

            U->>F: Click "Generate Plan"
            F->>B: POST /ai/generate-plan
            B->>C: Queue task via Celery
            C->>A: Request plan from LLM
            A-->>C: Return generated plan
            C-->>B: Task complete
            B-->>W: Emit progress/status
            W-->>F: Realtime updates
            F-->>U: Show plan results
        """,
    },
}
