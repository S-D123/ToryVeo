from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import requests

from ..models import Scene
import subprocess
from src.utils.cli import spinner_status

@dataclass
class VoiceoverGenerator:
    elevenlabs_api_key: str | None
    elevenlabs_voice_id: str | None
    elevenlabs_model_id: str
    piper_path: str
    timeout_seconds: int = 60
    session: requests.Session = field(default_factory=requests.Session)

    def generate_for_scene(self, scene: Scene, output_path: Path) -> None:
        if self.elevenlabs_api_key != "your_elevenlabs_api_key" and self.elevenlabs_voice_id:
            with spinner_status(f"Piper working on scene {scene.scene_number}") as status:                
                self._generate_elevenlabs(scene.narration, output_path)
                status.update("")
            return
        
        else:
            # fallback(use piper.gpl)
            with spinner_status(f"Piper working on scene {scene.scene_number}") as status:
                self.generate_using_piper(scene.narration, output_path)
                status.update("")
            return

        raise RuntimeError("No TTS API key configured for ElevenLabs or Piper.")

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

    def generate_using_piper(self, text: str, output_path: str) -> None:

        # call piper here
        try:
            result = subprocess.run(["python", self.piper_path, "--text", text, "--output", output_path], timeout=self.timeout_seconds)
            # print(result)
        except Exception as e:
            print(e)
            raise

def generate_voiceovers(
    scenes: Iterable[Scene],
    generator: VoiceoverGenerator,
    output_dir: Path,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for scene in scenes:
        output_path = output_dir / f"scene_{scene.scene_number}.mp3"
        
        # only generate audio file, if audio file not already present/created
        if not Path.is_file(output_path):
            generator.generate_for_scene(scene, output_path)
            generated.append(output_path)
            
    return generated
