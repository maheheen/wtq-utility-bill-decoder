"""One function: call(cfg, system, user_text, image_path, schema) -> dict, with retries and a disk cache."""
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageOps
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from src.config import CACHE_DIR, ModelCfg

MAX_SIDE = 2400


def prepare_image(image_path: Path) -> bytes:
    """EXIF-rotate, cap the long side at MAX_SIDE (never upscale), return PNG bytes."""
    img = ImageOps.exif_transpose(Image.open(image_path)).convert("RGB")
    long_side = max(img.size)
    if long_side > MAX_SIDE:
        scale = MAX_SIDE / long_side
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _cache_key(cfg: ModelCfg, system: str, user_text: str, image_bytes: bytes, schema: dict) -> str:
    h = hashlib.sha256()
    for part in (image_bytes, system.encode(), user_text.encode(),
                 cfg.provider.encode(), cfg.model.encode(), json.dumps(schema, sort_keys=True).encode()):
        h.update(hashlib.sha256(part).digest())
    return h.hexdigest()


def _retryable(exc: BaseException) -> bool:
    if isinstance(exc, json.JSONDecodeError):
        return True
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    return code == 429 or (isinstance(code, int) and code >= 500)


@retry(retry=retry_if_exception(_retryable), stop=stop_after_attempt(4),
       wait=wait_exponential(multiplier=2, min=2, max=30), reraise=True)
def _generate(cfg: ModelCfg, system: str, user_text: str, image_png: bytes, schema: dict) -> dict:
    if cfg.provider != "google":
        raise NotImplementedError(f"provider {cfg.provider!r} not wired yet, add it when the bake-off needs it")
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=cfg.api_key)
    resp = client.models.generate_content(
        model=cfg.model,
        contents=[types.Part.from_bytes(data=image_png, mime_type="image/png"), user_text],
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=cfg.temperature,
            seed=0,
            response_mime_type="application/json",
            response_json_schema=schema,
        ),
    )
    return json.loads(resp.text)


def call(cfg: ModelCfg, system: str, user_text: str, image_path: str | Path, schema: dict) -> dict:
    image_png = prepare_image(Path(image_path))
    path = CACHE_DIR / f"{_cache_key(cfg, system, user_text, image_png, schema)}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    result = _generate(cfg, system, user_text, image_png, schema)
    CACHE_DIR.mkdir(exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return result
