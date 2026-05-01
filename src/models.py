from __future__ import annotations

from pydantic import BaseModel, Field


class Scene(BaseModel):
    scene_number: int = Field(..., ge=1)
    narration: str
    image_prompt: str
