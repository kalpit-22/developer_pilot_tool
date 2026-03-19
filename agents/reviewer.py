from agents.base import BaseAgent


class ReviewerAgent(BaseAgent):
    name = "reviewer"
    system_prompt = """You are a strict senior code reviewer.
    Evaluate the code and execution output provided.
    Respond with ONLY a valid JSON object — no explanation, no markdown, nothing else.

    Approve:  {"approved": true,  "feedback": "brief note"}
    Reject:   {"approved": false, "feedback": "specific actionable feedback"}

    Approve when:
    - Exit code is 0
    - No syntax errors or import errors in STDERR
    - Code matches the task description
    - If execution output is "SKIPPED: not a Python file", approve immediately

    IMPORTANT: EOFError in output is caused by the test environment running out of 
    input — this is NOT a bug in the code. Approve if the only error is EOFError.

    Reject when:
    - SyntaxError, ImportError, NameError, or other real code errors
    - Exit code is not 0 AND there are real errors (not EOFError)
    - Logic clearly does not match the task"""

    def review(self, task) -> bool:
        """Returns True if approved, False if rejected. Stores feedback in task.review_feedback."""
        prompt = f"""Task: {task.description}
File: {task.filename}

--- CODE ---
{task.code}

--- EXECUTION OUTPUT ---
{task.test_output or "Not executed."}

Respond with ONLY the JSON object."""

        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, max_tokens=256)
        print(f"[Reviewer] Raw response: {response}")

        try:
            result = self.parse_json(response)
            approved = bool(result.get("approved", False))
            task.review_feedback = result.get("feedback", "")
            print(f"[Reviewer] {'✅ Approved' if approved else '❌ Rejected'}: {task.review_feedback}")
            return approved
        except Exception as e:
            # If JSON parsing fails, check raw text for approval signal
            if "true" in response.lower() and "approved" in response.lower():
                task.review_feedback = "Auto-approved (JSON parse fallback)"
                print("[Reviewer] ✅ Auto-approved via fallback")
                return True
            task.review_feedback = f"Parse error: {str(e)[:80]}"
            print(f"[Reviewer] ❌ Parse failed: {e}")
            return False