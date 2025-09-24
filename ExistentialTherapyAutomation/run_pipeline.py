#!/usr/bin/env python3
import os, sys, argparse, yaml, traceback
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

from pipeline import PhilosophyPipeline

console = Console()

def parse_args():
    p = argparse.ArgumentParser(description="Run the multi-language philosophy pipeline.")
    p.add_argument("question", nargs="?", help="Your philosophical question (English).")
    p.add_argument("--file", help="Read the question from a text file.")
    p.add_argument("--dry-run", action="store_true", help="Do not call the API; produce mock outputs.")
    p.add_argument("--with-ru", action="store_true", help="Enable Russian for this run even if disabled in config.")
    p.add_argument("--with-ja", action="store_true", help="Enable Japanese for this run even if disabled in config.")
    p.add_argument("--config", default="config.yaml", help="Path to config file.")
    return p.parse_args()

def load_question(args) -> str:
    if args.question:
        return args.question.strip()
    if args.file:
        return Path(args.file).read_text(encoding="utf-8").strip()
    console.print("[red]No question provided. Pass a string or --file path.[/red]")
    sys.exit(1)

def main():
    load_dotenv()
    args = parse_args()
    question = load_question(args)

    cfg_path = Path(args.config)
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    else:
        cfg = {}

    # per-run toggles
    if "languages" in cfg:
        for lang in cfg["languages"]:
            if args.with_ru and lang.get("code")=="ru":
                lang["enabled"] = True
            if args.with_ja and lang.get("code")=="ja":
                lang["enabled"] = True

    pipe = PhilosophyPipeline(cfg=cfg, dry_run=args.dry_run)
    try:
        result = pipe.run(question_en=question)
    except Exception as e:
        console.print(Panel.fit(str(e), title="Error", style="red"))
        traceback.print_exc()
        sys.exit(2)

    out = pipe.save_journal(result)
    console.print(Panel.fit(f"Saved journal → {out}", title="Done", style="green"))

if __name__ == "__main__":
    main()
