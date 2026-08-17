"""
Captain AI OS — Hugging Face Image Generation Tool
Pattern ported from: ge-ai-apps/imageapp/myimage.py
Model: black-forest-labs/FLUX.1-schnell via HuggingFace InferenceClient
Fallback: Pollinations.ai (free, no key needed)
"""

import io
import time
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional

import httpx
from loguru import logger
from config import settings


def _get_hf_client():
    """Lazily initialize HuggingFace InferenceClient (same pattern as imageapp/myimage.py)."""
    try:
        from huggingface_hub import InferenceClient
        api_key = settings.hf_api_key
        if not api_key:
            logger.warning("HF_API_KEY not set. HuggingFace image generation unavailable.")
            return None
        return InferenceClient(api_key=api_key)
    except ImportError:
        logger.warning("huggingface_hub not installed. Run: pip install huggingface-hub")
        return None


def generate_image_hf(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate image using FLUX.1-schnell via HuggingFace InferenceClient.
    Exact same logic as imageapp/myimage.py — generate_image().
    Saves output to data/outputs/ and returns the file path.

    Args:
        prompt:   Text description of the image
        width:    Output width in pixels (default: 1024)
        height:   Output height in pixels (default: 1024)
        filename: Optional custom filename (auto-generated if None)

    Returns:
        Dict with status, image_path, engine, prompt
    """
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)
    out_filename = filename or f"img_{abs(hash(prompt)) % 100000}_{int(time.time())}.png"
    out_path = settings.outputs_dir / out_filename

    # --- Primary: HuggingFace FLUX.1-schnell ---
    client = _get_hf_client()
    if client:
        try:
            model = settings.hf_image_model  # black-forest-labs/FLUX.1-schnell
            logger.info(f"HF ImageGen: Generating via {model} | prompt='{prompt[:60]}...'")

            pil_image = client.text_to_image(
                prompt=prompt,
                model=model,
                width=width,
                height=height
            )

            # Save PIL image to disk (same as imageapp)
            pil_image.save(str(out_path), format="PNG")

            logger.info(f"HF ImageGen: Saved to {out_path}")
            return {
                "status": "success",
                "prompt": prompt,
                "engine": f"huggingface/{model.split('/')[-1]}",
                "image_path": str(out_path.resolve()),
                "width": width,
                "height": height,
            }

        except Exception as e:
            logger.warning(f"HF ImageGen failed: {e} — falling back to Pollinations")

    # --- Fallback: Pollinations.ai (free, no key) ---
    try:
        logger.info(f"Pollinations fallback: Generating image for '{prompt[:60]}...'")
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        with httpx.Client(timeout=40.0, follow_redirects=True, headers=headers) as client_http:
            resp = client_http.get(url)
            resp.raise_for_status()

        out_path.write_bytes(resp.content)
        logger.info(f"Pollinations fallback: Saved to {out_path}")

        return {
            "status": "success",
            "prompt": prompt,
            "engine": "pollinations",
            "image_path": str(out_path.resolve()),
            "width": width,
            "height": height,
        }

    except Exception as e:
        logger.error(f"Both HF and Pollinations image generation failed: {e}")
        return {
            "status": "error",
            "prompt": prompt,
            "error": str(e),
        }


def get_supported_styles() -> Dict[str, str]:
    """
    Return the style preset suffixes from imageapp reference.
    Used by ImageAgent to append style tags to prompts.
    """
    return {
        "photorealistic": ", photorealistic, 8k, studio lighting",
        "cinematic": ", cinematic still, dramatic lighting",
        "anime": ", anime aesthetic, detailed line art",
        "cyberpunk": ", cyberpunk style, neon lighting, futuristic",
        "digital art": ", digital art, concept art, highly detailed",
        "3d render": ", 3d render, octane render, smooth, ultra HD",
    }
