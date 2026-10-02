#!/usr/bin/env python3
"""Generate or edit images through the Qiniu Modelink API (OpenAI-compatible).

Routes:
  - openai/gpt-image-*          -> POST /v1/images/generations | /v1/images/edits
  - google/gemini-*-image*      -> POST /v1/chat/completions (image_config)

Stdlib only; Python 3.9+. The API key is resolved from (never logged):
  1. --api-key
  2. MODELINK_API_KEY environment variable
  3. ~/.modelink/.env
  4. .env files found walking up from the working directory, then the script's directory
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = "https://api.qnaigc.com/v1"
DEFAULT_MODEL = "openai/gpt-image-2"
GPT_IMAGE_MODELS = [
    "openai/gpt-image-2",
    "openai/gpt-image-2.5-flare",
    "openai/gpt-image-2.5-sunburst",
]
SIZE_PRESETS = [
    "1024x1024", "1536x1024", "1024x1536",
    "2048x2048", "2048x1152", "3840x2160", "2160x3840",
]
ASPECT_RATIOS = ["1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3",
                 "4:5", "5:4", "8:1", "9:16", "16:9", "21:9"]
IMAGE_SIZES = ["512", "1K", "2K", "4K"]
MIME_BY_EXT = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".webp": "image/webp", ".gif": "image/gif",
}
EXT_BY_MIME = {
    "image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif",
}
USER_AGENT = "lora-generate-image-skill/1.0"


# ---------------------------------------------------------------- credentials

def load_env_file(path):
    """Parse KEY=VALUE lines; returns dict. Ignores comments and blanks."""
    values = {}
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return values
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip().strip("'\"")
    return values


def find_dotenv():
    """First .env walking up from cwd, else the one next to this script."""
    here = Path(__file__).resolve().parent
    for start in [Path.cwd(), *Path.cwd().parents, here, *here.parents]:
        candidate = start / ".env"
        if candidate.is_file():
            return candidate
    return None


def resolve_api_key(cli_value):
    if cli_value:
        return cli_value
    env = os.environ.get("MODELINK_API_KEY")
    if env:
        return env
    home_env = Path.home() / ".modelink" / ".env"
    key = load_env_file(home_env).get("MODELINK_API_KEY")
    if key:
        return key
    dotenv = find_dotenv()
    if dotenv:
        key = load_env_file(dotenv).get("MODELINK_API_KEY")
        if key:
            return key
    return None


def require_key(args):
    key = resolve_api_key(args.api_key)
    if key:
        return key
    sys.stderr.write(
        "Error: no API key found. Set it in one of these ways (never hardcode it):\n"
        "  1. export MODELINK_API_KEY=sk-...            (environment variable)\n"
        f"  2. put 'MODELINK_API_KEY=sk-...' in {Path.home() / '.modelink' / '.env'}\n"
        "  3. put it in a .env file in the working directory (must stay gitignored)\n"
        "  4. pass --api-key for one-off use\n"
        "Keys are created in the Modelink console (https://modelink.ai).\n"
    )
    sys.exit(1)


# ------------------------------------------------------------------- routing

def route_for(model):
    """gemini image models use the chat endpoint; everything else images endpoints."""
    return "chat" if "gemini" in model.lower() else "images"


# -------------------------------------------------------------- input images

def read_reference(source):
    """Return (url_or_data_uri, label). Local files become base64 data URIs."""
    if source.startswith(("http://", "https://", "data:")):
        return source, source if source.startswith("data:") else Path(source).name
    path = Path(source)
    if not path.is_file():
        sys.stderr.write(f"Error: reference image not found: {source}\n")
        sys.exit(1)
    mime = MIME_BY_EXT.get(path.suffix.lower())
    if not mime:
        sys.stderr.write(
            f"Error: unsupported reference format {path.suffix!r} "
            "(png, jpeg, webp, gif are accepted): {source}\n".format(source=source)
        )
        sys.exit(1)
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}", path.name


# ------------------------------------------------------------- validation

def validate_size(size):
    if size == "auto":
        return
    m = re.fullmatch(r"(\d+)x(\d+)", size)
    if not m:
        sys.stderr.write(
            f"Error: --size must be 'auto', WxH, or one of: {', '.join(SIZE_PRESETS)}\n"
        )
        sys.exit(1)
    w, h = int(m.group(1)), int(m.group(2))
    problems = []
    if w <= 0 or h <= 0:
        problems.append("width and height must be positive")
    if w % 16 or h % 16:
        problems.append("width and height must be multiples of 16")
    if max(w, h) > 3840:
        problems.append("max side must not exceed 3840")
    if min(w, h) > 0 and max(w, h) / min(w, h) > 3:
        problems.append("long/short side ratio must not exceed 3:1")
    if not 655360 <= w * h <= 8294400:
        problems.append("total pixels must be 655,360-8,294,400")
    if problems:
        sys.stderr.write(f"Error: invalid --size {size}: " + "; ".join(problems) + "\n")
        sys.exit(1)


def check_route_params(args):
    """Fail fast, before any billed request, on parameters the route ignores."""
    route = route_for(args.model)
    problems = []
    if route == "images":
        if args.aspect_ratio:
            problems.append(f"--aspect-ratio only applies to gemini models (use --size)")
        if args.resolution:
            problems.append(f"--resolution only applies to gemini models (use --size)")
    else:
        if args.size:
            problems.append("--size only applies to gpt-image models (use --aspect-ratio/--resolution)")
        if args.quality:
            problems.append("--quality only applies to gpt-image models")
        if args.background:
            problems.append("--background only applies to gpt-image models")
        if args.aspect_ratio and args.aspect_ratio not in ASPECT_RATIOS:
            problems.append(f"--aspect-ratio must be one of: {', '.join(ASPECT_RATIOS)}")
        if args.resolution and args.resolution not in IMAGE_SIZES:
            problems.append(f"--resolution must be one of: {', '.join(IMAGE_SIZES)}")
    if args.output_compression is not None:
        if args.output_format not in ("jpeg", "webp"):
            problems.append("--output-compression requires --output-format jpeg|webp")
    if problems:
        sys.stderr.write("Error: request rejected before calling the API:\n")
        for p in problems:
            sys.stderr.write(f"  - {p}\n")
        sys.exit(1)


# ------------------------------------------------------------------ requests

def http_json(url, payload, key, timeout, retries):
    """POST JSON, retrying 429/5xx and network errors. Never logs the key."""
    body = json.dumps(payload).encode("utf-8")
    last_error = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")
            retryable = e.code == 429 or e.code >= 500
            last_error = f"HTTP {e.code}: {detail.strip() or e.reason}"
            if not retryable:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_error = f"network error: {e}"
        if attempt < retries:
            time.sleep(2 ** attempt)
    sys.stderr.write(f"Error: request failed after {retries + 1} attempt(s): {last_error}\n")
    sys.exit(1)


def build_images_payload(args, references):
    payload = {"model": args.model, "prompt": args.prompt}
    if args.size:
        payload["size"] = args.size
    if args.quality:
        payload["quality"] = args.quality
    if args.background:
        payload["background"] = args.background
    if args.output_format:
        payload["output_format"] = args.output_format
    if args.output_compression is not None:
        payload["output_compression"] = args.output_compression
    if args.n is not None:
        payload["n"] = args.n
    if references:
        payload["image"] = [ref for ref, _ in references]
    return payload


def build_chat_payload(args, references):
    content = [{"type": "text", "text": args.prompt}]
    for ref, _ in references:
        content.append({"type": "image_url", "image_url": {"url": ref}})
    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": content}],
        "modalities": ["image", "text"],
    }
    image_config = {}
    if args.aspect_ratio:
        image_config["aspect_ratio"] = args.aspect_ratio
    if args.resolution:
        image_config["image_size"] = args.resolution
    if args.output_format:
        image_config["image_output_options"] = {
            "mime_type": "image/png" if args.output_format == "png" else "image/jpeg"
        }
    if image_config:
        payload["image_config"] = image_config
    return payload


def summarize_body(payload):
    """Dry-run view: replace base64 payloads with size annotations."""
    def shrink(value):
        if isinstance(value, str) and len(value) > 120:
            return f"<{len(value)} chars, base64 or long text>"
        if isinstance(value, list):
            return [shrink(v) for v in value]
        if isinstance(value, dict):
            return {k: shrink(v) for k, v in value.items()}
        return value
    return shrink(payload)


# ------------------------------------------------------------------- output

def decode_image(item):
    """Return (bytes, extension). Accepts b64_json or a data/HTTP URL."""
    b64 = item.get("b64_json")
    if b64:
        return base64.b64decode(re.sub(r"\s+", "", b64)), ".png"
    url = (item.get("image_url") or {}).get("url") or item.get("url")
    if url and url.startswith("data:"):
        header, _, payload = url.partition(",")
        mime = header.partition(":")[2].partition(";")[0] or "image/png"
        return base64.b64decode(re.sub(r"\s+", "", payload)), EXT_BY_MIME.get(mime, ".png")
    if url:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=120
        ) as resp:
            mime = resp.headers.get("Content-Type", "image/png").partition(";")[0]
            return resp.read(), EXT_BY_MIME.get(mime, ".png")
    raise ValueError("response item carries neither b64_json nor a url")


def write_images(items, out_path, explicit_ext, requested_format):
    ext = explicit_ext or (f".{requested_format}" if requested_format else None)
    written = []
    for i, item in enumerate(items, 1):
        data, default_ext = decode_image(item)
        ext = ext or default_ext
        if len(items) > 1:
            stem, suffix = (out_path.stem, out_path.suffix) if out_path.suffix \
                else (out_path.name, ext)
            target = out_path.with_name(f"{stem}_{i}{suffix or ext}")
        else:
            target = out_path if out_path.suffix else out_path.with_name(out_path.name + ext)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        written.append(target)
    return written


def print_usage(usage):
    if not usage:
        return
    fields = [
        ("total_tokens", "total tokens"), ("input_tokens", "input tokens"),
        ("output_tokens", "output tokens"), ("ti_quantity", "generated images"),
        ("ii_quantity", "edited images (single ref)"), ("mi2i_quantity", "edited images (multi ref)"),
        ("req_count", "billed requests"),
    ]
    parts = [f"{label}: {usage[name]}" for name, label in fields if usage.get(name) is not None]
    if parts:
        print("Usage — " + ", ".join(parts))


# ------------------------------------------------------------------ helpers

def list_models(args, base_url):
    url = f"{base_url}/models"
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"Error: HTTP {e.code} listing models\n")
        sys.exit(1)
    ids = sorted(m.get("id", "") for m in data.get("data", []))
    needle = (args.list_models or "").lower()
    if needle:
        ids = [i for i in ids if needle in i.lower()]
    if not ids:
        print("No matching models.")
        return
    print("Models on Modelink (image models are routed automatically by name):")
    for i in ids:
        mark = "  [image]" if "image" in i.lower() else ""
        print(f"  {i}{mark}")
    print(
        "\nGPT Image models (images endpoints, not always listed above):\n"
        + "\n".join(f"  {m}" for m in GPT_IMAGE_MODELS)
    )


# --------------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(
        description="Generate or edit images via Qiniu Modelink (GPT Image 2 / Gemini).",
        epilog="Examples:\n"
               '  %(prog)s "sunset over mountains, photorealistic"\n'
               '  %(prog)s "make the sky purple" -i photo.jpg -o edited.png\n'
               '  %(prog)s "poster bg" -m openai/gpt-image-2 --size 1536x1024 --quality high\n'
               '  %(prog)s "mascot" -m google/gemini-3.1-flash-image --aspect-ratio 16:9\n'
               '  %(prog)s "test" --dry-run',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("prompt", nargs="?", help="image description or edit instruction")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL,
                        help=f"default: {DEFAULT_MODEL}")
    parser.add_argument("-o", "--output", default=None,
                        help="output path (default: generated_image.<ext> in cwd)")
    parser.add_argument("-i", "--input", action="append", default=[], dest="inputs",
                        help="reference image: local path, URL, or data URL (repeatable, max 16)")
    parser.add_argument("--n", type=int, default=None,
                        help="number of images per request (gpt-image models; upstream passthrough)")
    parser.add_argument("--size", default=None,
                        help="auto | WxH (16-multiples, <=3840, ratio<=3:1) | preset like 1536x1024 (gpt-image)")
    parser.add_argument("--quality", default=None,
                        help="low | medium | high | auto (gpt-image; 2.5 also xhigh/max)")
    parser.add_argument("--background", default=None,
                        help="auto | transparent | opaque (gpt-image)")
    parser.add_argument("--output-format", default=None, choices=["png", "jpeg", "webp"],
                        help="output container (default png)")
    parser.add_argument("--output-compression", type=int, default=None,
                        help="0-100, jpeg/webp only")
    parser.add_argument("--aspect-ratio", default=None,
                        help="1:1, 16:9, 9:16, ... (gemini models)")
    parser.add_argument("--resolution", default=None,
                        help="512 | 1K | 2K | 4K (gemini models)")
    parser.add_argument("--api-key", default=None, help="override key resolution")
    parser.add_argument("--base-url", default=None,
                        help=f"override API base (default {DEFAULT_BASE_URL})")
    parser.add_argument("--timeout", type=int, default=300, help="seconds per request")
    parser.add_argument("--retries", type=int, default=2, help="retries for 429/5xx/network")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the request without sending it (no key needed)")
    parser.add_argument("--list-models", nargs="?", const="", default=None, metavar="FILTER",
                        help="list model IDs, optionally filtered by substring, then exit")
    args = parser.parse_args()

    base_url = (args.base_url or os.environ.get("MODELINK_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")

    if args.list_models is not None:
        list_models(args, base_url)
        return

    if not args.prompt:
        parser.error("a prompt is required (or use --list-models / --dry-run with a prompt)")
    if len(args.inputs) > 16:
        sys.stderr.write("Error: at most 16 reference images per request.\n")
        sys.exit(1)

    check_route_params(args)
    if args.size:
        validate_size(args.size)

    references = [read_reference(src) for src in args.inputs]
    route = route_for(args.model)
    payload = (build_images_payload(args, references) if route == "images"
               else build_chat_payload(args, references))

    if args.dry_run:
        endpoint = "/images/edits" if (route == "images" and references) else \
                   "/images/generations" if route == "images" else "/chat/completions"
        print(f"POST {base_url}{endpoint}")
        print(json.dumps(summarize_body(payload), indent=2, ensure_ascii=False))
        print("(dry run — nothing sent, nothing billed)")
        return

    key = require_key(args)
    endpoint = "/images/edits" if (route == "images" and references) else \
               "/images/generations" if route == "images" else "/chat/completions"

    print(f"Generating with {args.model} ({len(references)} reference image(s))...")
    response = http_json(f"{base_url}{endpoint}", payload, key, args.timeout, args.retries)

    if route == "images":
        items = response.get("data") or []
    else:
        message = (response.get("choices") or [{}])[0].get("message") or {}
        items = message.get("images") or []
        if not items:
            text = message.get("content") or response.get("error", {}).get("message", "")
            sys.stderr.write(
                "Error: the model returned no image" +
                (f"; it said: {text}" if text else ".") +
                "\nRephrase the prompt (content policy rejections usually arrive this way).\n"
            )
            sys.exit(2)

    out_path = Path(args.output) if args.output else Path.cwd() / "generated_image"
    explicit_ext = Path(args.output).suffix.lower() if args.output else None
    written = write_images(items, out_path, explicit_ext, args.output_format)

    for path in written:
        print(f"Wrote {path} ({path.stat().st_size} bytes)")
    print_usage(response.get("usage"))


if __name__ == "__main__":
    main()
