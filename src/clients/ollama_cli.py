from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .llm_client import LLMClient


@dataclass
class OllamaCliClient(LLMClient):
    model: str
    cli_path: str = "ollama"
    temperature: float = 0.2

    def generate(self, prompt: str) -> str:
        cli_path = self._resolve_cli_path()
        command = [cli_path, "run", self.model]
        env = {
            **os.environ,
            "OLLAMA_TEMPERATURE": str(self.temperature),
        }

        result = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            check=True,
            env=env,
            encoding="utf-8",
            errors="replace",
        )
        # return result.stdout.strip()
        return result

    def _resolve_cli_path(self) -> str:
        print("Path Error:", self.cli_path)
        return "ollama"
