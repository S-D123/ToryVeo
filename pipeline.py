from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

from src.clients.ollama_cli import OllamaCliClient
from src.config import ensure_output_dir, load_settings
from src.models import Scene
from src.phases.image_generation import ComfyUIClient, generate_images
from src.phases.story_breakdown import StoryBreakdown, StoryBreakdownResult
from src.phases.video_assembly import VideoSettings, assemble_video
from src.phases.voiceover_generation import VoiceoverGenerator, generate_voiceovers


def run_phase1(story_path: Path, output_path: Path) -> list[Scene]:
    settings = load_settings()
    ensure_output_dir(settings.output_dir)

    # added later
    if Path.is_file(output_path): 
        print("story_scenes.json file already present")
        return load_scenes(output_path)

    story_text = story_path.read_text(encoding="utf-8")

    client = OllamaCliClient(
        model=settings.ollama_model,
        cli_path=settings.ollama_cli_path,
        temperature=settings.ollama_temperature,
    )
    breaker = StoryBreakdown(llm_client=client)

    # just for cli viz
    console = Console()
    with console.status(
        "[bold green]Breaking story into scenes",
        spinner="dots",
        spinner_style="status.spinner",
        speed=1.0
    ) as status:
    # cli viz ends
        result = breaker.run(story_text)
        status.update("Saving scene")
        breaker.save(result, output_path)
        
    return result.scenes


def load_scenes(scene_json: Path) -> list[Scene]:
    payload = json.loads(scene_json.read_text(encoding="utf-8"))
    return [Scene.model_validate(item) for item in payload]


def run_phase2(scenes: list[Scene]) -> list[Path]:
    settings = load_settings()
    ensure_output_dir(settings.output_dir)

    client = ComfyUIClient(
        base_url=settings.comfyui_api_url,
        workflow_path=settings.comfyui_workflow_path,
        prompt_node_id=settings.comfyui_prompt_node_id,
        seed=settings.comfyui_seed,
    )
    return generate_images(scenes, client, settings.output_dir)


def run_phase3(scenes: list[Scene]) -> list[Path]:
    settings = load_settings()
    ensure_output_dir(settings.output_dir)

    generator = VoiceoverGenerator(
        elevenlabs_api_key=settings.elevenlabs_api_key,
        elevenlabs_voice_id=settings.elevenlabs_voice_id,
        elevenlabs_model_id=settings.elevenlabs_model_id,
        piper_path=settings.piper_path
    )
    return generate_voiceovers(scenes, generator, settings.output_dir)


def run_phase4(scenes: list[Scene]) -> Path:
    settings = load_settings()
    ensure_output_dir(settings.output_dir)

    video_settings = VideoSettings(
        resolution=settings.video_resolution,
        fps=settings.video_fps,
        zoom_start=settings.video_zoom_start,
        zoom_end=settings.video_zoom_end,
    )
    return assemble_video(
        scenes=scenes,
        assets_dir=settings.output_dir,
        output_path=settings.video_output,
        settings=video_settings,
    )


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent
    story_file = root_dir / "story.txt"
    output_file = root_dir / "assets" / "story_scenes.json"

    if not story_file.exists():
        raise FileNotFoundError("story.txt not found at project root.")

    scenes = run_phase1(story_file, output_file)
    print(f"Phase 1 complete. Wrote {output_file}")

    image_paths = run_phase2(scenes)
    print(f"Phase 2 complete. Generated {len(image_paths)} images.")

    audio_paths = run_phase3(scenes)
    print(f"Phase 3 complete. Generated {len(audio_paths)} audio files.")

    video_path = run_phase4(scenes)
    print(f"Phase 4 complete. Wrote {video_path}")
