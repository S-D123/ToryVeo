# Module Architecture

## Pipeline Phases

### Phase 1: Story Breakdown
**Module:** `src/phases/story_breakdown.py`  
**Input:** Plain text story  
**Outputs:** JSON array saved to `assets/story_scenes.json` with fields:
	- `scene_number` (int)
	- `narration` (string)
	- `image_prompt` (string, always appended with the style tag)
**What it does:** Uses Ollama CLI to parse story into numbered scenes with narration text and image prompts.

---

### Phase 2: Image Generation
**Module:** `src/phases/image_generation.py`  
**Input:** List of scenes with image prompts  
**Output:** `assets/scene_#.png` (one PNG per scene)  
**What it does:** Injects prompts into ComfyUI workflow, calls Stable Diffusion API, downloads generated images.

---

### Phase 3: Voiceover Generation
**Module:** `src/phases/voiceover_generation.py`  
**Input:** List of scenes with narration text  
**Output:** `assets/scene_#.mp3` (one MP3 per scene)  
**What it does:** Generates audio narration using ElevenLabs API (or OpenAI TTS fallback; Piper WIP).

---

### Phase 4: Video Assembly
**Module:** `src/phases/video_assembly.py`  
**Input:** Scene images + audio files  
**Output:** `final_story.mp4`  
**What it does:** Combines images and audio into MP4 video with Ken Burns (pan & zoom) effect using MoviePy.

---

## Key Support Modules

| Module | Purpose |
|--------|---------|
| `src/models.py` | Data classes: `Scene`, `StoryBreakdownResult` |
| `src/config.py` | Load settings from `.env` and environment |
| `src/clients/ollama_cli.py` | Ollama CLI wrapper; implements `LLMClient` protocol |
| `src/utils/cli.py` | Rich spinner context manager for CLI feedback |

---

## Entry Point

**`pipeline.py`:**
- `run_phase1()` – Break story into scenes
- `run_phase2()` – Generate images
- `run_phase3()` – Generate voiceovers
- `run_phase4()` – Assemble video
- `load_scenes()` – Load cached scenes from JSON

Call these functions in sequence or load cached results to resume interrupted runs.