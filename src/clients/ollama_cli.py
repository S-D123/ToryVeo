from __future__ import annotations

import requests
from dataclasses import dataclass
from pathlib import Path

from .llm_client import LLMClient


@dataclass
class OllamaCliClient(LLMClient):
    model: str
    cli_path: str = "ollama"
    temperature: float = 0.2

    def generate(self, prompt: str) -> str:
        # previously used subprocess.run

        url = "http://localhost:11434/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature
            }
        }

        try:
            # send POST request
            res = requests.post(url, json=payload)
            res.raise_for_status() # raises http errors
            
            return res.json().get("response", "").strip()
        
        except Exception as e:
            print(f"Exception [ollama_cli.py] : {e}")

    def _resolve_cli_path(self) -> str:
        print("Path Error:", self.cli_path)
        # return part needs fix/improvement
        return "ollama"
