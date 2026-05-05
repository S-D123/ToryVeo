# Offline Ollama setup for StoryBreakdown

This file contains guidance for installing and configuring Ollama locally for offline story breakdowns.

## Why this is manual
Ollama’s installer and model files are large binaries and must be downloaded from Ollama’s official distribution.

## Windows installation (offline-friendly)
1. On a machine with internet access, download the latest Ollama Windows installer from:
   https://ollama.com/download
2. Copy the installer to this machine (USB, LAN share, etc.).
3. Run the installer and confirm `ollama` is available in your PATH:
   - Open PowerShell and run: `ollama --version`

## Download models for offline use
1. With internet access on the same machine (or temporarily connected), pull the model you plan to use:
   - Example: `ollama pull phi3:mini`
2. Once the model is pulled, Ollama can run it offline.

## Configure `StoryBreakdown`
Update your `.env` to point to the local Ollama CLI:
```
OLLAMA_MODEL=phi3:mini
OLLAMA_CLI_PATH=ollama
OLLAMA_TEMPERATURE=0.2
```

## Quick validation
Run the pipeline phase 1 to verify:
- Put a story in `story.txt`
- Run `pipeline.py`
- Expect: `assets/story_scenes.json`

## Optional: Custom Ollama install path
If `ollama` is not in PATH, set a full path:
```
OLLAMA_CLI_PATH=C:\...\Ollama\ollama.exe
```
