# Story-to-Video Content Pipeline

ToryVeo is a pipeline that can be used to generate animated videos for kids from a story.

## How it works

The input has to be a story. The story is given to Ollama, which breaks the whole story into scenes. The scenes are given to StableDiffusion/Flux Models to generate an image for the scene. The scenes are then given to TTS(Text-to-Speech) engine like piper for narration. Lastly, all the scenes are combined using moviepy/FFMPEG.

## What's included
- Phase 1: Story breakdown into structured JSON using Ollama CLI.
- Phase 2: Image generation via ComfyUI API.
- Phase 3: Voiceover generation with ElevenLabs (OpenAI fallback).
- Phase 4: Video assembly with Ken Burns effect.

## Setup
1. Create a virtual environment (Python 3.10.13).
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and fill in your API keys.
4. Provide a ComfyUI workflow JSON at `workflows/comfyui_workflow.json`.
Note: You do require Ollama, Flux Model, and TTS Model to run locally. Also, I have used phi3:mini, but can use any other models

## Usage (so far)
- Place your story in `story.txt` at the repo root.
- Run `pipeline.py` to execute phases 1–3.

## Module documentation
### `src/phases/story_breakdown.py` (Phase 1)
- **Purpose:** Converts raw story text into structured scene data using an LLM.
- **Key class:** `StoryBreakdown`.
- **Inputs:** Raw story text string.
- **Outputs:** JSON array saved to `assets/story_scenes.json` with fields:
	- `scene_number` (int)
	- `narration` (string)
	- `image_prompt` (string, always appended with the style tag)
- **LLM client:** `OllamaCliClient` in `src/clients/ollama_cli.py` (swappable via `LLMClient` protocol).
- **Validation:** Ensures JSON array structure and sequential scene numbering.

### `src/phases/image_generation.py` (Phase 2)
- **Purpose:** Generates images for each scene using a ComfyUI API.
- **Key class:** `ComfyUIClient`.
- **Inputs:** `Scene.image_prompt` and a ComfyUI workflow JSON.
- **Outputs:** Sequential PNG images (`assets/scene_#.png`).
- **Notes:** Uses `COMFYUI_PROMPT_NODE_ID` to locate the prompt node in the workflow and updates `seed` inputs when present.

### `src/phases/voiceover_generation.py` (Phase 3)
- **Purpose:** Generates voiceover audio for each scene.
- **Key class:** `VoiceoverGenerator`.
- **Primary provider:** ElevenLabs (requires `ELEVENLABS_API_KEY` + `ELEVENLABS_VOICE_ID`).
- **Fallback:** OpenAI TTS if ElevenLabs isn’t configured.
- **Outputs:** Sequential MP3 files (`assets/scene_#.mp3`).

### `pipeline.py`
- **Purpose:** Orchestrates phases 1–4 end-to-end.
- **Flow:** Reads `story.txt` → generates `story_scenes.json` → generates images → generates audio → renders video.

### `src/phases/video_assembly.py` (Phase 4)
- **Purpose:** Builds the final MP4 using MoviePy with a Ken Burns effect.
- **Key functions:** `assemble_video`, `make_ken_burns_clip`.
- **Inputs:** `assets/scene_#.png` + `assets/scene_#.mp3`.
- **Outputs:** `final_story.mp4` (configurable via `VIDEO_OUTPUT`).
- **Ken Burns behavior:** Gentle zoom from `VIDEO_ZOOM_START` to `VIDEO_ZOOM_END` with a small alternating pan per scene.

### Phase 4 requirements
- **FFmpeg:** MoviePy requires FFmpeg on your PATH. Install FFmpeg separately and verify it is available.
- **Python:** Use Python 3.10.13 for best wheel support on Windows.
