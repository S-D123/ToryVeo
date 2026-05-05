from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import urllib
from src.utils.cli import spinner_status

import requests

from ..models import Scene


@dataclass
class ComfyUIClient:
    base_url: str
    workflow_path: Path
    prompt_node_id: str
    seed: int = 1234
    timeout_seconds: int = 45
    poll_interval: float = 1.5
    session: requests.Session = field(default_factory=requests.Session)

    def generate_image(self, image_prompt: str, output_path: Path) -> None:
        workflow = self._load_workflow()
        workflow = self._inject_prompt(workflow, image_prompt)
        workflow = self._inject_seed(workflow)

        # updated code(instead of using session.post)
        try:
            response = urllib.request.Request(
                f"{self.base_url}/prompt",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=json.dumps(workflow).encode('utf-8')
            )

            with urllib.request.urlopen(response) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                prompt_id = res_data["prompt_id"]
                if not prompt_id:
                    raise RuntimeError("ComfyUI did not return a prompt_id")

                image_info = self._wait_for_image(prompt_id)
                image_bytes = self._download_image(image_info)
                output_path.write_bytes(image_bytes)

        except Exception as e:
            print("Exception:", e)

    def _load_workflow(self) -> dict[str, Any]:
        if not self.workflow_path.exists():
            raise FileNotFoundError(
                f"ComfyUI workflow not found at {self.workflow_path}. Provide it in .env."
            )
        return json.loads(self.workflow_path.read_text(encoding="utf-8"))

    def _inject_prompt(self, workflow: dict[str, Any], image_prompt: str) -> dict[str, Any]:
        prompt_node = workflow.get("prompt", {}).get(self.prompt_node_id)
        if not prompt_node:
            raise KeyError(
                f"Prompt node '{self.prompt_node_id}' not found in workflow JSON."
            )
        prompt_node.setdefault("inputs", {})["text"] = image_prompt
        return workflow

    def _inject_seed(self, workflow: dict[str, Any]) -> dict[str, Any]:
        for node in workflow.get("prompt", {}).values():
            if isinstance(node, dict) and isinstance(node.get("inputs"), dict):
                if "seed" in node["inputs"]:
                    node["inputs"]["seed"] = self.seed
        return workflow

    def _wait_for_image(self, prompt_id: str) -> dict[str, Any]:
        deadline = time.time() + self.timeout_seconds
        history_url = f"{self.base_url}/history/{prompt_id}"
        while time.time() < deadline:
            response = self.session.get(history_url, timeout=self.timeout_seconds)
            response.raise_for_status()
            history = response.json()
            outputs = history.get(prompt_id, {}).get("outputs", {})
            for output in outputs.values():
                images = output.get("images") if isinstance(output, dict) else None
                if images:
                    return images[0]
            time.sleep(self.poll_interval)
        raise TimeoutError("Timed out waiting for image generation from ComfyUI")

    def _download_image(self, image_info: dict[str, Any]) -> bytes:
        filename = image_info.get("filename")
        subfolder = image_info.get("subfolder", "")
        image_type = image_info.get("type", "output")
        if not filename:
            raise ValueError("Invalid image info from ComfyUI history response")
        params = {"filename": filename, "subfolder": subfolder, "type": image_type}
        response = self.session.get(f"{self.base_url}/view", params=params, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.content


def generate_images(
    scenes: list[Scene],
    client: ComfyUIClient,
    output_dir: Path,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for scene in scenes:
        output_path = output_dir / f"scene_{scene.scene_number}.png"

        # generate an image only if the image is not already created
        if not Path.is_file(output_path):
            with spinner_status(f"Generating image for scene {scene.scene_number}") as status:
                client.generate_image(scene.image_prompt, output_path)
                generated.append(output_path)
                status.update("")
    return generated
