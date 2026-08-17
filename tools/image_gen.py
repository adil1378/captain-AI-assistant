import urllib.parse
from pathlib import Path
from typing import Dict, Any
import httpx
from loguru import logger
from src.backend.config import settings

_OUTPUTS_DIR = Path("./data/outputs")


def generate_image(prompt: str, filename: str = None) -> Dict[str, Any]:
    """Generate image from text prompt using specified engine (Pollinations / HuggingFace / OpenAI)."""
    try:
        _OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        out_filename = filename or f"image_{abs(hash(prompt)) % 10000}.png"
        out_path = _OUTPUTS_DIR / out_filename

        engine = getattr(settings, "IMAGE_GEN_ENGINE", "pollinations").lower()

        if engine in ["pollinations", "huggingface", "free"]:
            # If Hugging Face token is available, use HF inference API; otherwise use Pollinations AI free generator
            hf_token = getattr(settings, "HF_TOKEN", "")
            if engine == "huggingface" and hf_token:
                api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
                headers = {"Authorization": f"Bearer {hf_token}"}
                with httpx.Client(timeout=45.0, headers=headers) as client:
                    resp = client.post(api_url, json={"inputs": prompt})
                    if resp.status_code == 200:
                        out_path.write_bytes(resp.content)
                        logger.info(f"Image successfully generated via Hugging Face: {out_path.resolve()}")
                        return {
                            "status": "success",
                            "prompt": prompt,
                            "engine": "huggingface",
                            "image_path": str(out_path.resolve())
                        }

            # Pollinations AI High-Quality Free Engine
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            with httpx.Client(timeout=35.0, follow_redirects=True, headers=headers) as client:
                resp = client.get(url)
                resp.raise_for_status()

            out_path.write_bytes(resp.content)
            logger.info(f"Image successfully generated via Pollinations: {out_path.resolve()}")

            return {
                "status": "success",
                "prompt": prompt,
                "engine": "pollinations",
                "image_path": str(out_path.resolve())
            }

        elif engine == "openai":
            openai_key = getattr(settings, "OPENAI_API_KEY", "")
            if not openai_key:
                return {"status": "error", "error": "OPENAI_API_KEY is required for OpenAI image generation."}
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            with httpx.Client(timeout=30.0) as http_client:
                img_data = http_client.get(image_url).content
            out_path.write_bytes(img_data)
            return {
                "status": "success",
                "prompt": prompt,
                "engine": "openai",
                "image_path": str(out_path.resolve())
            }
        else:
            return {"status": "error", "error": f"Unsupported image engine: {engine}"}

    except Exception as e:
        logger.error(f"Image generation failed for prompt '{prompt}': {e}")
        return {"status": "error", "error": str(e)}
