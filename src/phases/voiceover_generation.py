from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import requests
from openai import OpenAI

from ..models import Scene


@dataclass
class VoiceoverGenerator:
    elevenlabs_api_key: str | None
    elevenlabs_voice_id: str | None
    elevenlabs_model_id: str
    openai_api_key: str | None
    openai_tts_model: str
    openai_tts_voice: str
    timeout_seconds: int = 60
    session: requests.Session = field(default_factory=requests.Session)

    def generate_for_scene(self, scene: Scene, output_path: Path) -> None:
        if self.elevenlabs_api_key and self.elevenlabs_voice_id:
            self._generate_elevenlabs(scene.narration, output_path)
            return
        if self.openai_api_key:
            self._generate_openai(scene.narration, output_path)
            return
        raise RuntimeError("No TTS API key configured for ElevenLabs or OpenAI.")

    def _generate_elevenlabs(self, text: str, output_path: Path) -> None:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
        headers = {
            "xi-api-key": self.elevenlabs_api_key,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": self.elevenlabs_model_id,
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.8},
        }
        response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout_seconds)
        response.raise_for_status()
        output_path.write_bytes(response.content)

    def _generate_openai(self, text: str, output_path: Path) -> None:
        client = OpenAI(api_key=self.openai_api_key)
        response = client.audio.speech.create(
            model=self.openai_tts_model,
            voice=self.openai_tts_voice,
            input=text,
            format="mp3",
        )
        output_path.write_bytes(response.content)


def generate_voiceovers(
    scenes: Iterable[Scene],
    generator: VoiceoverGenerator,
    output_dir: Path,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for scene in scenes:
        output_path = output_dir / f"scene_{scene.scene_number}.mp3"
        generator.generate_for_scene(scene, output_path)
        generated.append(output_path)
    return generated
