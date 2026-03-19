from dataclasses import dataclass, field
from agents.base import BaseAgent


@dataclass
class Task:
    id: str
    description: str
    filename: str
    dependencies: list[str] = field(default_factory=list)
    code: str = ""
    test_output: str = ""
    review_feedback: str = ""
    status: str = "pending"   # pending | done | failed
    retries: int = 0


class PlannerAgent(BaseAgent):
    name = "planner"
    system_prompt = """You are a software architect. Break a request into a minimal list of coding tasks.

    Rules:
    - Use as many files as the problem genuinely needs — no more, no less
    - Simple single-concern tools (converters, generators, organizers) need ONE file
    - Only split into multiple files when there are genuinely separate concerns
    - Only add a third file if there is a genuinely separate concern (e.g. utilities, data models)
    - Each task maps to ONE file
    - Prefer simple solutions over clever ones
    - Respond ONLY with a valid JSON array, no explanation, no markdown

    Schema:
    [
    {
        "id": "task_1",
        "description": "What to build",
        "filename": "src/module.py",
        "dependencies": []
    }
    ]"""

    def plan(self, request: str) -> list[Task]:
        """Ask the model to break the request into tasks, return list of Task objects."""
        messages = [
            {"role": "user", "content": f"Break this into coding tasks:\n\n{request}"}
        ]

        raw = self.chat(messages, max_tokens=1024)
        # print(f"[Planner] Raw response:\n{raw}\n")

        items = self.parse_json(raw)

        tasks = []
        for item in items:
            tasks.append(Task(
                id=item["id"],
                description=item["description"],
                filename=item.get("filename", f"{item['id']}.py"),
                dependencies=item.get("dependencies", []),
            ))

        return tasks

    def plan(self, request: str) -> list[Task]:
        """Ask the model to break the request into tasks, return list of Task objects."""
        messages = [
            {"role": "user", "content": f"Break this into coding tasks:\n\n{request}"}
        ]

        raw = self.chat(messages, max_tokens=1024)
        print(f"[Planner] Raw response:\n{raw}\n")

        items = self.parse_json(raw)

        tasks = []
        for item in items:
            tasks.append(Task(
                id=item["id"],
                description=item["description"],
                filename=item.get("filename", f"{item['id']}.py"),
                dependencies=item.get("dependencies", []),
            ))

        return tasks