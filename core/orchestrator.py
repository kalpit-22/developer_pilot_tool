"""
Orchestrator — manages the full DevPilot pipeline.

Flow:
  Planner -> (Coder -> Executor -> Reviewer) x N tasks -> save to output/
"""

import asyncio
import os
import shutil
import pathlib
from dataclasses import dataclass, field
from typing import Optional

from agents.planner   import PlannerAgent, Task
from agents.coder     import CoderAgent
from agents.executor  import ExecutorAgent, WORKSPACE
from agents.reviewer  import ReviewerAgent

MAX_RETRIES = 3
OUTPUT_DIR  = pathlib.Path("output")


class Orchestrator:

    def __init__(self, provider: str = "deepseek"):
        self.provider = provider
        self.planner  = PlannerAgent()
        self.executor = ExecutorAgent()
        self.reviewer = ReviewerAgent()
        self.files: dict[str, str] = {}        # filename -> code

    async def run(self, request: str) -> dict:
        print(f"\n🚀 Starting Developer Pilot tool")
        print(f"Request: {request}\n")

        # ── Clean up from previous run ────────────────────────────────────
        if WORKSPACE.exists():
            shutil.rmtree(WORKSPACE)
        WORKSPACE.mkdir()

        # ── Phase 1: Plan ─────────────────────────────────────────────────
        print("─── PLANNING ───")
        tasks = self.planner.plan(request)
        print(f"Created {len(tasks)} task(s):")
        for t in tasks:
            print(f"  [{t.id}] {t.description} -> {t.filename}")

        # ── Phase 2: Code -> Execute -> Review each task ──────────────────
        for task in tasks:
            await self._process_task(task, request)

        # ── Phase 3: Save to output/ ──────────────────────────────────────
        done   = [t for t in tasks if t.status == "done"]
        failed = [t for t in tasks if t.status == "failed"]

        print(f"\n{'─' * 40}")
        print(f"Done:   {len(done)} task(s)")
        print(f"Failed: {len(failed)} task(s)")

        if self.files:
            OUTPUT_DIR.mkdir(exist_ok=True)
            for filename, code in self.files.items():
                fpath = OUTPUT_DIR / filename
                fpath.parent.mkdir(parents=True, exist_ok=True)
                fpath.write_text(code, encoding="utf-8")
                print(f"  Saved: {fpath}")
            print(f"\nAll files saved to ./{OUTPUT_DIR}/")

        return {"tasks": tasks, "files": self.files}

    async def _process_task(self, task: Task, request: str):
        print(f"\n─── TASK [{task.id}]: {task.description} ───")

        for attempt in range(1, MAX_RETRIES + 1):
            if attempt > 1:
                print(f"\n  Retry {attempt}/{MAX_RETRIES}")
                print(f"  Feedback: {task.review_feedback}")

            # ── Code ──────────────────────────────────────────────────────
            print("  [CODING]")
            context = self._build_context()
            coder = CoderAgent()
            coder.code(task, context)
            if not task.code:
                print("  Coder produced no code — skipping task.")
                break

            # ── Execute ───────────────────────────────────────────────────
            print("  [EXECUTING]")
            await self.executor.execute(task, written_files=self.files)

            # ── Review ────────────────────────────────────────────────────
            print("  [REVIEWING]")
            approved = self.reviewer.review(task)

            if approved:
                task.status = "done"
                self.files[task.filename] = task.code
                return

        task.status = "failed"
        print(f"  Task [{task.id}] failed after {MAX_RETRIES} attempts")

    def _build_context(self) -> str:
        if not self.files:
            return "No files written yet."
        return "\n\n".join(
            f"### {fname}\n```python\n{code}\n```"
            for fname, code in self.files.items()
        )