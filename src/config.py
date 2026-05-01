from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    ollama_model: str
    ollama_cli_path: str
    ollama_temperature: float
    comfyui_api_url: str
    comfyui_workflow_path: Path
    comfyui_prompt_node_id: str
    comfyui_seed: int
    elevenlabs_api_key: str | None
    elevenlabs_voice_id: str | None
    elevenlabs_model_id: str
    openai_api_key: str | None
    openai_tts_model: str
    openai_tts_voice: str
    output_dir: Path
    video_resolution: tuple[int, int]
    video_fps: int
    video_zoom_start: float
    video_zoom_end: float
    video_output: Path


def _get_env_float(key: str, default: float) -> float:
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid float for {key}: {value}") from exc


def _get_env_int(key: str, default: int) -> int:
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid int for {key}: {value}") from exc


def _get_env_resolution(key: str, default: tuple[int, int]) -> tuple[int, int]:
    value = os.getenv(key)
    if not value:
        return default
    match = value.lower().replace(" ", "").split("x")
    if len(match) != 2:
        raise ValueError(f"Invalid resolution format for {key}: {value}")
    try:
        return int(match[0]), int(match[1])
    except ValueError as exc:
        raise ValueError(f"Invalid resolution format for {key}: {value}") from exc


def load_settings() -> Settings:
    load_dotenv()

    root_dir = Path(__file__).resolve().parents[1]
    output_dir = Path(os.getenv("OUTPUT_DIR", "assets"))
    if not output_dir.is_absolute():
        output_dir = root_dir / output_dir

    workflow_path = Path(os.getenv("COMFYUI_WORKFLOW_PATH", "workflows/comfyui_workflow.json"))
    if not workflow_path.is_absolute():
        workflow_path = root_dir / workflow_path

    video_output = Path(os.getenv("VIDEO_OUTPUT", "final_story.mp4"))
    if not video_output.is_absolute():
        video_output = root_dir / video_output

    return Settings(
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1"),
        ollama_cli_path=os.getenv("OLLAMA_CLI_PATH", "ollama"),
        ollama_temperature=_get_env_float("OLLAMA_TEMPERATURE", 0.2),
        comfyui_api_url=os.getenv("COMFYUI_API_URL", "http://127.0.0.1:8188"),
        comfyui_workflow_path=workflow_path,
        comfyui_prompt_node_id=os.getenv("COMFYUI_PROMPT_NODE_ID", "6"),
        comfyui_seed=_get_env_int("COMFYUI_SEED", 1234),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
        elevenlabs_model_id=os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_tts_model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
        openai_tts_voice=os.getenv("OPENAI_TTS_VOICE", "alloy"),
        output_dir=output_dir,
        video_resolution=_get_env_resolution("VIDEO_RESOLUTION", (1920, 1080)),
        video_fps=_get_env_int("VIDEO_FPS", 24),
        video_zoom_start=_get_env_float("VIDEO_ZOOM_START", 1.0),
        video_zoom_end=_get_env_float("VIDEO_ZOOM_END", 1.1),
        video_output=video_output,
    )


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
