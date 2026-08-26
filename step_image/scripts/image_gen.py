#!/usr/bin/env python3
"""CLI for StepFun image generation and editing."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import requests

BASE_URL = "https://api.stepfun.com/step_plan/v1"
DEFAULT_MODEL = "step-image-edit-2"
DEFAULT_SIZE = "1024x1024"
DEFAULT_OUTPUT_PATH = "output/step_image/output.png"
ALLOWED_SIZES = {
    "1024x1024",
    "768x1360",
    "896x1184",
    "1360x768",
    "1184x896",
}
MAX_N = 4


def die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def ensure_api_key(dry_run: bool = False) -> None:
    if os.getenv("STEP_API_KEY"):
        return
    if dry_run:
        print("Warning: STEP_API_KEY is not set; dry-run only.", file=sys.stderr)
        return
    die("STEP_API_KEY is not set. Export it before running.")


def validate_size(size: str) -> None:
    if size not in ALLOWED_SIZES:
        die(f"size must be one of: {', '.join(sorted(ALLOWED_SIZES))}")


def build_output_paths(out: str, count: int, ext: str = "png") -> list[Path]:
    base = Path(out)
    if count == 1:
        return [base if base.suffix else base.with_suffix(f".{ext}")]
    paths = []
    for i in range(1, count + 1):
        p = base if base.suffix else base.with_suffix(f".{ext}")
        paths.append(p.with_name(f"{p.stem}-{i}{p.suffix}"))
    return paths


def decode_and_write(images: list[str], outputs: list[Path], force: bool = False) -> None:
    for idx, b64 in enumerate(images):
        if idx >= len(outputs):
            break
        out_path = outputs[idx]
        if out_path.exists() and not force:
            die(f"Output already exists: {out_path} (use --force to overwrite)")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(base64.b64decode(b64))
        print(f"Wrote {out_path}")


def _headers() -> dict[str, str]:
    key = os.getenv("STEP_API_KEY", "")
    if not key:
        die("STEP_API_KEY is not set. Export it before running.")
    return {
        "Authorization": f"Bearer {key}",
    }


def _request_with_retries(method: str, url: str, *, retries: int = 3, **kwargs):
    session = requests.Session()
    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            resp = session.request(method, url, timeout=120, **kwargs)
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 2 ** attempt))
                print(f"Rate limited. Retrying in {retry_after}s...", file=sys.stderr)
                time.sleep(min(retry_after, 60))
                continue
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            last_exc = exc
            if attempt == retries:
                break
            sleep_s = min(60.0, 2.0 ** attempt)
            print(f"Attempt {attempt}/{retries} failed: {exc}. Retrying in {sleep_s:.1f}s", file=sys.stderr)
            time.sleep(sleep_s)
    raise last_exc or RuntimeError("unknown error")


def generate(args: argparse.Namespace) -> None:
    prompt = args.prompt.strip()
    if not prompt:
        die("Missing prompt. Use --prompt.")

    validate_size(args.size)
    ensure_api_key(args.dry_run)

    payload = {
        "model": args.model,
        "prompt": prompt,
        "n": args.n,
        "size": args.size,
        "response_format": "b64_json",
    }

    if args.cfg_scale is not None:
        payload["cfg_scale"] = args.cfg_scale
    if args.steps is not None:
        payload["steps"] = args.steps
    if args.seed is not None:
        payload["seed"] = args.seed
    if args.text_mode:
        payload["text_mode"] = True

    if args.dry_run:
        print(json.dumps({"endpoint": "/v1/images/generations", **payload}, indent=2))
        return

    outputs = build_output_paths(args.out, args.n)

    print("Calling StepFun image generation...", file=sys.stderr)
    resp = _request_with_retries("POST", f"{BASE_URL}/images/generations", json=payload, headers=_headers())
    result = resp.json()

    images = [item["b64_json"] for item in result.get("data", []) if item.get("b64_json")]
    if not images:
        die("No images returned.")

    decode_and_write(images, outputs, force=args.force)
    print("Generation completed.")


def edit(args: argparse.Namespace) -> None:
    prompt = args.prompt.strip()
    if not prompt:
        die("Missing prompt. Use --prompt.")

    if not args.image:
        die("Missing input image(s). Use --image.")

    validate_size(args.size)
    ensure_api_key(args.dry_run)

    files = []
    for path in args.image:
        p = Path(path)
        if not p.exists():
            die(f"Image file not found: {p}")
        files.append(("image", (p.name, p.open("rb"), "application/octet-stream")))

    data = {
        "model": args.model,
        "prompt": prompt,
        "size": args.size,
        "response_format": "b64_json",
    }

    if args.cfg_scale is not None:
        data["cfg_scale"] = str(args.cfg_scale)
    if args.steps is not None:
        data["steps"] = str(args.steps)
    if args.seed is not None:
        data["seed"] = str(args.seed)
    if args.text_mode:
        data["text_mode"] = "true"

    if args.dry_run:
        preview = {
            "endpoint": "/v1/images/edits",
            "files": [f[1][0] for f in files],
            **data,
        }
        print(json.dumps(preview, indent=2))
        return

    outputs = build_output_paths(args.out, 1)

    print(f"Calling StepFun image edit with {len(files)} image(s)...", file=sys.stderr)
    resp = _request_with_retries("POST", f"{BASE_URL}/images/edits", headers=_headers(), files=files, data=data)
    result = resp.json()

    images = [item["b64_json"] for item in result.get("data", []) if item.get("b64_json")]
    if not images:
        die("No images returned.")

    decode_and_write(images, outputs, force=args.force)
    print("Edit completed.")


def add_shared_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--prompt", required=True, help="Text prompt for the image.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL}).")
    parser.add_argument("--size", default=DEFAULT_SIZE, help=f"Image size (default: {DEFAULT_SIZE}).")
    parser.add_argument("--n", type=int, default=1, help=f"Number of images (default: 1, max: {MAX_N}).")
    parser.add_argument("--out", default=DEFAULT_OUTPUT_PATH, help="Output file path.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing output files.")
    parser.add_argument("--dry-run", action="store_true", help="Print the request without sending it.")
    parser.add_argument("--cfg-scale", type=float, help="Classifier-free guidance scale.")
    parser.add_argument("--steps", type=int, help="Number of inference steps.")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility.")
    parser.add_argument("--text-mode", action="store_true", help="Enable text-optimized generation.")


def main() -> int:
    parser = argparse.ArgumentParser(description="StepFun image generation and editing CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate", help="Generate an image from a prompt")
    add_shared_args(gen_parser)
    gen_parser.set_defaults(func=generate)

    edit_parser = subparsers.add_parser("edit", help="Edit an existing image")
    add_shared_args(edit_parser)
    edit_parser.add_argument("--image", action="append", required=True, help="Input image path(s).")
    edit_parser.set_defaults(func=edit)

    args = parser.parse_args()
    if args.n < 1 or args.n > MAX_N:
        die(f"--n must be between 1 and {MAX_N}")

    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
