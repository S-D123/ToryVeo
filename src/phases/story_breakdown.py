from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pydantic import ValidationError

from ..clients.llm_client import LLMClient
from ..models import Scene

DEFAULT_STYLE_TAG = "watercolor children's book illustration"


@dataclass
class StoryBreakdownResult:
    scenes: list[Scene]
    raw_response: str


@dataclass
class StoryBreakdown:
    llm_client: LLMClient
    style_tag: str = DEFAULT_STYLE_TAG

    def build_prompt(self, story_text: str) -> str:
        return (
            "You are a helpful assistant that converts children's stories into structured scene data.\n"
            "Return ONLY a valid JSON array. No extra commentary.\n\n"
            "Requirements for each array item:\n"
            "- scene_number: integer starting at 1\n"
            "- narration: exact text to be spoken for the scene\n"
            "- image_prompt: a highly descriptive prompt for image generation\n\n"
            "After crafting each image_prompt, append the style tag: "
            f"'{self.style_tag}'.\n\n"
            "Story text:\n"
            f"{story_text.strip()}\n"
        )

    def run(self, story_text: str) -> StoryBreakdownResult:
        prompt = self.build_prompt(story_text)
        raw_response = self.llm_client.generate(prompt)
        scenes = self._parse_scenes(raw_response)
        return StoryBreakdownResult(scenes=scenes, raw_response=raw_response)

    def save(self, result: StoryBreakdownResult, output_path: Path) -> None:
        payload = [scene.model_dump() for scene in result.scenes]
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _parse_scenes(self, raw_response: str) -> list[Scene]:
        json_text = self._extract_json(raw_response)
        json_text = self._sanitize_json(json_text)
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM response is not valid JSON: {exc}") from exc

        if not isinstance(data, list):
            raise ValueError("LLM response must be a JSON array")

        scenes: list[Scene] = []
        for item in data:
            try:
                scene = Scene.model_validate(item)
            except ValidationError as exc:
                raise ValueError(f"Invalid scene entry: {exc}") from exc

            scene = scene.copy(update={"image_prompt": self._append_style(scene.image_prompt)})
            scenes.append(scene)

        self._validate_scene_numbers(scenes)
        return scenes

    def _append_style(self, prompt: str) -> str:
        if self.style_tag.lower() in prompt.lower():
            return prompt
        cleaned = prompt.strip().rstrip(".")
        return f"{cleaned}. {self.style_tag}"

    def _extract_json(self, raw_response: str) -> str:
        match = re.search(r"\[.*\]", raw_response, re.DOTALL)
        if not match:
            raise ValueError("Could not find JSON array in LLM response")
        return match.group(0)

    def _sanitize_json(self, json_text: str) -> str:
        # Remove ASCII control characters that break JSON parsing.
        return re.sub(r"[\x00-\x1F\x7F]", "", json_text)

    def _validate_scene_numbers(self, scenes: Iterable[Scene]) -> None:
        expected = 1
        for scene in sorted(scenes, key=lambda item: item.scene_number):
            if scene.scene_number != expected:
                raise ValueError(
                    f"Scene numbers must be sequential starting at 1. Missing {expected}."
                )
            expected += 1
