from agents.base import BaseAgent

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read an existing file for context before writing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Path of file to read"}
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write complete code to a file. Always call this to save your work.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Path of file to write"},
                    "content":  {"type": "string", "description": "Complete file content"},
                },
                "required": ["filename", "content"],
            },
        },
    },
]


class CoderAgent(BaseAgent):
    name = "coder"
    system_prompt = """You are a senior Python engineer. Write simple, minimal, working code.

    Rules:
    - KISS — Keep It Simple. Use the simplest solution that solves the problem
    - No unnecessary classes, abstractions, or helper functions
    - No more code than what the task explicitly asks for
    - Complete files only — no placeholders or TODOs
    - Absolute imports only — never relative imports
    - No interactive input() calls — use argparse or hardcoded defaults
    - Plain ASCII only — no emojis or special characters
    - Call write_file to save your code
    """
    def __init__(self):
        self._written: dict[str, str] = {}

    def code(self, task, context: str) -> None:
        self._written = {}

        feedback = (
            f"\nPrevious reviewer feedback to fix:\n{task.review_feedback}"
            if task.review_feedback else ""
        )

        prompt = f"""Task: {task.description}
File to write: {task.filename}

Existing codebase:
{context if context else "No files written yet."}
{feedback}

Call write_file with the complete code for {task.filename}."""

        messages = [{"role": "user", "content": prompt}]
        final_text, tool_calls = self.chat_with_tools(messages, TOOLS)

        for call in tool_calls:
            if call["tool"] == "write_file":
                task.code = call["input"]["content"]
                task.filename = call["input"]["filename"]
                print(f"[Coder] ✅ Wrote {task.filename} ({len(task.code)} chars)")
                return

        print(f"[Coder] ❌ Failed. Response was:\n{final_text[:200]}")

    def _handle_tool(self, name: str, inp: dict) -> str:
        if name == "write_file":

            # Handle variations in argument names
            filename = inp.get("filename") or inp.get("file_name") or inp.get("path")
            content  = inp.get("content")  or inp.get("code")      or inp.get("file_content") or ""

            if not filename:
                return "Error: no filename provided."

            self._written[filename] = content
            return f"Wrote {filename} successfully."

        if name == "read_file":
            filename = inp.get("filename") or inp.get("file_name") or inp.get("path", "")
            if filename in self._written:
                return self._written[filename]
            try:
                with open(filename, encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                return f"File not found: {filename}"

        return f"Unknown tool: {name}"