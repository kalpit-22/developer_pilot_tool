"""
ExecutorAgent — runs generated code in a persistent workspace folder.

"""

import asyncio
import os
import sys
import shutil
import pathlib


WORKSPACE = pathlib.Path("workspace")
TIMEOUT = 15

# Dummy stdin values fed to every run — covers most input() scenarios
TEST_INPUT = b""

def prepare_workspace(files: dict[str, str]) -> None:
    """
    Write all completed files into the workspace folder.
    Creates __init__.py in every subdirectory so imports work.
    Called by the Orchestrator before executing each task.
    """
    WORKSPACE.mkdir(exist_ok=True)

    # Always ensure src/__init__.py exists
    (WORKSPACE / "src").mkdir(exist_ok=True)
    (WORKSPACE / "src" / "__init__.py").touch()

    for filename, code in files.items():
        fpath = WORKSPACE / filename
        fpath.parent.mkdir(parents=True, exist_ok=True)

        # Create __init__.py in every package directory
        for parent in fpath.parents:
            if parent == WORKSPACE:
                break
            init = parent / "__init__.py"
            if not init.exists():
                init.touch()

        fpath.write_text(code, encoding="utf-8")


def write_task_file(task) -> pathlib.Path:
    """Write the current task's code into the workspace and return its path."""
    fpath = WORKSPACE / task.filename
    fpath.parent.mkdir(parents=True, exist_ok=True)

    # Ensure __init__.py exists in every parent dir inside workspace
    for parent in fpath.parents:
        if parent == WORKSPACE:
            break
        init = parent / "__init__.py"
        if not init.exists():
            init.touch()

    fpath.write_text(task.code, encoding="utf-8")
    return fpath


def build_env() -> dict:
    """Build a clean environment for the subprocess."""
    env = os.environ.copy()
    # PYTHONPATH = workspace root so 'from src.x import' resolves
    env["PYTHONPATH"] = str(WORKSPACE.resolve())
    # Force UTF-8 everywhere — prevents emoji/unicode crashes on Windows
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return env


def file_to_module(filename: str) -> str:
    """
    Convert a file path to a Python module string.
    e.g. 'src/game.py' -> 'src.game'
         'main.py'     -> 'main'
    """
    return pathlib.Path(filename).with_suffix("").as_posix().replace("/", ".")


async def run_subprocess(
    args: list[str],
    cwd: pathlib.Path,
    env: dict,
) -> tuple[str, str, int]:
    """Run a subprocess and return (stdout, stderr, returncode)."""
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
        cwd=str(cwd),
        env=env,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=TEST_INPUT),
            timeout=TIMEOUT,
        )
        return (
            stdout.decode("utf-8", errors="replace"),
            stderr.decode("utf-8", errors="replace"),
            proc.returncode,
        )
    except asyncio.TimeoutError:
        proc.kill()
        return "", f"TIMEOUT: execution exceeded {TIMEOUT}s", -1


class ExecutorAgent:
    name = "executor"

    async def execute(self, task, written_files: dict[str, str] = None) -> None:
        """
        Execute task.code in the workspace and store output in task.test_output.

        """
        if not task.filename.endswith(".py"):
            task.test_output = "SKIPPED: not a Python file"
            print(f"[Executor] Skipped {task.filename}")
            return
        if not task.code:
            task.test_output = "ERROR: No code to execute."
            return

        # Set up workspace with all files
        prepare_workspace(written_files or {})
        write_task_file(task)
        env = build_env()
        module = file_to_module(task.filename)

        # ── Strategy 1: run as module (handles all import styles) ────────────
        stdout, stderr, returncode = await run_subprocess(
            [sys.executable, "-m", module],
            cwd=WORKSPACE,
            env=env,
        )

        # ── Strategy 2: if module run failed with import error, try direct ───

        if returncode != 0 and (
            "ImportError" in stderr
            or "ModuleNotFoundError" in stderr
            or "No module named '__main__'" in stderr
        ):
            print(f"[Executor] Module run failed, trying direct file execution...")
            stdout2, stderr2, returncode2 = await run_subprocess(
                [sys.executable, str(WORKSPACE / task.filename)],
                cwd=WORKSPACE,
                env=env,
            )
            # Use whichever run produced a better result
            if returncode2 == 0 or len(stderr2) < len(stderr):
                stdout, stderr, returncode = stdout2, stderr2, returncode2

        # ── Format output for Reviewer ───────────────────────────────────────
        parts = []
        if stdout.strip():
            parts.append(f"STDOUT:\n{stdout}")
        if stderr.strip():
            parts.append(f"STDERR:\n{stderr}")
        parts.append(f"EXIT CODE: {returncode}")
        task.test_output = "\n".join(parts)

        print(f"[Executor] Exit code: {returncode}")