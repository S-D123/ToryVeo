# Story-to-Video Content Pipeline

ToryVeo is a pipeline that can be used to generate animated videos for kids from a text story.

## How it works

The input has to be a story in plain text. The story is given to Ollama, which breaks the whole story into scenes. The scenes are given to Image Generating Models using comfyUI to generate an image for the scene. The scenes are then given to TTS(Text-to-Speech) engine like piper for narration. Lastly, all the scenes are combined using moviepy.

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

> **Local Dependencies**
> 
> This pipeline requires the following services running locally, so choose models according to your hardware specifications (VRAM, RAM, CPU cores):
> - **Ollama** – for story breakdown (any model, e.g., `mistral`, `neural-chat`)
> - **ComfyUI** – for image generation (with a compatible SD model checkpoint)
> - **TTS Model** – for voiceover generation (e.g., Piper or ElevenLabs API key)
> 
> **If image generation fails:**
> Image generation is computationally expensive and may consume significant RAM and VRAM. It may Throw `CUDA out of memory` or runtime exceptions and can cause system slowdowns or crashes. To prevent that, I would suggest:
>
> 1. Reduce resolution in `workflows/comfyui_workflow.json` (e.g., `512x512` → `256x256`)
> 2. Restart ComfyUI with memory optimization: `python main.py --lowram --cache-none`
> 3. Reduce steps for Ksmapler node. Suggested: 20-30, but you may reduce it.

## Usage (so far)
- Place your story in `story.txt` at the repo root.
- Run `pipeline.py` to execute phases 1–3.
