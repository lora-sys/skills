#!/usr/bin/env python3
from pathlib import Path
import argparse

BASE = Path(__file__).resolve().parents[1] / "assets" / "base-shell.html"

def main():
    parser = argparse.ArgumentParser(description="Scaffold a standalone teaching HTML deck.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--out", default="teaching-deck.html")
    args = parser.parse_args()
    text = BASE.read_text(encoding="utf-8").replace("{{TITLE}}", args.title)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(out)

if __name__ == "__main__":
    main()
