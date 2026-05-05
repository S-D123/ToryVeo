from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from moviepy import AudioFileClip, VideoClip, concatenate_videoclips
from PIL import Image

from ..models import Scene


@dataclass(frozen=True)
class VideoSettings:
    resolution: tuple[int, int] = (1920, 1080)
    fps: int = 24
    zoom_start: float = 1.0
    zoom_end: float = 1.1


def assemble_video(
    scenes: Iterable[Scene],
    assets_dir: Path,
    output_path: Path,
    settings: VideoSettings,
) -> Path:
    clips = []
    for scene in scenes:
        image_path = assets_dir / f"scene_{scene.scene_number}.png"
        audio_path = assets_dir / f"scene_{scene.scene_number}.mp3"
        if not image_path.exists():
            raise FileNotFoundError(f"Missing image for scene {scene.scene_number}: {image_path}")
        if not audio_path.exists():
            raise FileNotFoundError(f"Missing audio for scene {scene.scene_number}: {audio_path}")

        audio_clip = AudioFileClip(str(audio_path))
        duration = audio_clip.duration
        pan_start, pan_end = _choose_pan(scene.scene_number)
        clip = make_ken_burns_clip(
            image_path=image_path,
            duration=duration,
            resolution=settings.resolution,
            zoom_start=settings.zoom_start,
            zoom_end=settings.zoom_end,
            pan_start=pan_start,
            pan_end=pan_end,
        ).with_audio(audio_clip)
        clips.append(clip)

    final_clip = concatenate_videoclips(clips, method="compose")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_clip.write_videofile(
        str(output_path),
        fps=settings.fps,
        codec="libx264",
        audio_codec="aac",
    )
    final_clip.close()
    for clip in clips:
        clip.close()
    return output_path


def make_ken_burns_clip(
    image_path: Path,
    duration: float,
    resolution: tuple[int, int],
    zoom_start: float,
    zoom_end: float,
    pan_start: tuple[float, float],
    pan_end: tuple[float, float],
) -> VideoClip:
    image = Image.open(image_path).convert("RGB")
    base_w, base_h = image.size
    target_w, target_h = resolution
    base_scale = max(target_w / base_w, target_h / base_h)

    def make_frame(t: float) -> np.ndarray:
        progress = 1.0 if duration == 0 else min(max(t / duration, 0.0), 1.0)
        zoom = zoom_start + (zoom_end - zoom_start) * progress
        scale = base_scale * zoom
        resized_w = max(1, int(base_w * scale))
        resized_h = max(1, int(base_h * scale))
        resized = image.resize((resized_w, resized_h), Image.LANCZOS)

        pan_x = pan_start[0] + (pan_end[0] - pan_start[0]) * progress
        pan_y = pan_start[1] + (pan_end[1] - pan_start[1]) * progress
        center_x = int(resized_w * pan_x)
        center_y = int(resized_h * pan_y)
        left = _clamp(center_x - target_w // 2, 0, resized_w - target_w)
        top = _clamp(center_y - target_h // 2, 0, resized_h - target_h)
        crop = resized.crop((left, top, left + target_w, top + target_h))
        return np.array(crop)

    return VideoClip(make_frame, duration=duration)


def _choose_pan(scene_number: int) -> tuple[tuple[float, float], tuple[float, float]]:
    if scene_number % 2 == 0:
        return (0.55, 0.5), (0.45, 0.55)
    return (0.45, 0.5), (0.55, 0.55)


def _clamp(value: int, min_value: int, max_value: int) -> int:
    if max_value < min_value:
        return min_value
    return max(min_value, min(value, max_value))
