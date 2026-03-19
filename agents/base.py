import json
import re
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = "deepseek-chat"

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


class BaseAgent:
    name: str = "base"
    system_prompt: str = "You are a helpful assistant."

    def chat(self, messages: list[dict], max_tokens: int = 4096) -> str:
        """Simple one-shot chat. Returns plain text."""
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": self.system_prompt}] + messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    def chat_with_tools(self, messages: list[dict], tools: list[dict],
                        max_tokens: int = 4096) -> tuple[str, list[dict]]:
        """
        Agentic loop — keeps running until the model stops calling tools.
        Returns (final_text, list_of_tool_calls_made).
        """
        calls_made = []
        history = [{"role": "system", "content": self.system_prompt}] + messages

        for _ in range(20):
            response = client.chat.completions.create(
                model=MODEL,
                messages=history,
                tools=tools,
                tool_choice="auto",
                max_tokens=max_tokens,
            )
            msg = response.choices[0].message
            content = msg.content or ""

            # ── Model is done ─────────────────────────────────────────────
            if not msg.tool_calls:
                return content, calls_made

            # ── Model wants to call tools ─────────────────────────────────
            history.append({
                "role": "assistant",
                "content": content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            })

            for tc in msg.tool_calls:
                try:
                    tool_input = json.loads(tc.function.arguments)
                except Exception:
                    tool_input = {}

                result = self._handle_tool(tc.function.name, tool_input)
                calls_made.append({
                    "tool": tc.function.name,
                    "input": tool_input,
                    "result": result,
                })
                history.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(result),
                })

        return "", calls_made

    def _handle_tool(self, name: str, inp: dict) -> str:
        """Override in subclasses to handle specific tools."""
        return f"Tool '{name}' not implemented."

    def parse_json(self, text: str) -> dict | list:
        """Robustly extract JSON from a model response."""
        text = text.strip()
        # Strip markdown fences
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]).strip()
        # Extract first JSON object or array
        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if match:
            text = match.group(0)
        return json.loads(text)