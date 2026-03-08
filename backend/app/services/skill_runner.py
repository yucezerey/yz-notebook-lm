import asyncio
import sys
from pathlib import Path
from typing import Any

from app.config import SKILL_DIR, GENERATION_TIMEOUTS


class SkillRunnerError(Exception):
    def __init__(self, script: str, returncode: int, stderr: str):
        self.script = script
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"{script} failed (code {returncode}): {stderr[:200]}")


class SkillRunner:
    """Runs NotebookLM skill scripts as subprocesses via run.py wrapper."""

    RUN_PY = str(SKILL_DIR / "scripts" / "run.py")

    @staticmethod
    async def run(
        script: str,
        *args: str,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        if timeout is None:
            script_base = script.replace(".py", "")
            timeout = GENERATION_TIMEOUTS.get(script_base, 120)

        cmd = [sys.executable, SkillRunner.RUN_PY, script, *args]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(SKILL_DIR),
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            raise SkillRunnerError(script, -1, f"Timeout after {timeout}s")

        stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
        stderr = stderr_bytes.decode("utf-8", errors="replace").strip()

        if process.returncode != 0:
            raise SkillRunnerError(script, process.returncode, stderr or stdout)

        return {
            "stdout": stdout,
            "stderr": stderr,
            "returncode": process.returncode,
        }

    @staticmethod
    async def run_with_progress(
        script: str,
        *args: str,
        timeout: int | None = None,
    ):
        """Generator that yields stdout lines as they arrive (for WebSocket streaming)."""
        if timeout is None:
            script_base = script.replace(".py", "")
            timeout = GENERATION_TIMEOUTS.get(script_base, 120)

        cmd = [sys.executable, SkillRunner.RUN_PY, script, *args]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(SKILL_DIR),
        )

        try:
            async def read_lines():
                lines = []
                async for line in process.stdout:
                    decoded = line.decode("utf-8", errors="replace").strip()
                    if decoded:
                        lines.append(decoded)
                        yield decoded
                return lines

            async for line in read_lines():
                yield {"type": "progress", "message": line}

            await asyncio.wait_for(process.wait(), timeout=timeout)

            stderr = ""
            if process.stderr:
                stderr_bytes = await process.stderr.read()
                stderr = stderr_bytes.decode("utf-8", errors="replace").strip()

            if process.returncode != 0:
                yield {"type": "error", "message": stderr}
            else:
                yield {"type": "completed"}

        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            yield {"type": "error", "message": f"Timeout after {timeout}s"}
