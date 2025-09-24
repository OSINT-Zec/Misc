import os, json, yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import pytz

from prompts import (
    SYSTEM_TRANSLATOR, SYSTEM_COUNSELOR,
    USER_MAKE_GERMAN_PROMPT, USER_MAKE_FRENCH_PROMPT, USER_MAKE_RUSSIAN_PROMPT,
    USER_MAKE_ENGLISH_PROMPT, USER_MAKE_JAPANESE_PROMPT
)

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

DEFAULT_CFG = {
    "output_dir": "journal",
    "timezone": "Asia/Seoul",
    "languages": [
        {"code": "en", "name": "English", "enabled": True},
        {"code": "de", "name": "German", "enabled": True},
        {"code": "fr", "name": "French", "enabled": True},
        {"code": "ja", "name": "Japanese", "enabled": False},
        {"code": "ru", "name": "Russian", "enabled": False}
    ],
    "model_primary": "gpt-5",
    "model_fallbacks": ["gpt-4.1", "gpt-4o-mini"],
    "tone": {
        "counselor_style": "philosophical counselor; existential and meaning-centered; clear, concrete, non-therapeutic.",
        "translation_style": "faithful, clear, natural; preserve core terminology; avoid over-simplification."
    }
}

class PhilosophyPipeline:
    def __init__(self, cfg: Dict[str, Any], dry_run: bool=False):
        merged = DEFAULT_CFG.copy()
        merged.update(cfg or {})
        if "tone" in (cfg or {}):
            merged["tone"] = {**DEFAULT_CFG["tone"], **cfg["tone"]}
        self.cfg = merged
        self.dry_run = dry_run or bool(int(os.getenv("DRY_RUN", "0")))

        self.output_dir = Path(self.cfg["output_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tz = pytz.timezone(self.cfg["timezone"])

        self.models = [self.cfg["model_primary"]] + list(self.cfg.get("model_fallbacks", []))
        self.client = None
        if not self.dry_run:
            if OpenAI is None:
                raise RuntimeError("openai package not available. Install requirements or use --dry-run.")
            key = os.getenv("OPENAI_API_KEY", "").strip()
            if not key:
                raise RuntimeError("OPENAI_API_KEY not set. Put it in .env or your environment.")
            self.client = OpenAI(api_key=key)

    def _now_stamp(self) -> str:
        return datetime.now(self.tz).strftime("%Y-%m-%d_%H%M%S_kst")

    def _chat(self, messages: List[Dict[str, str]]) -> str:
        last_err = None
        for model in self.models:
            # Responses API
            try:
                resp = self.client.responses.create(model=model, input=messages)
                try:
                    return resp.output_text
                except Exception:
                    try:
                        return resp.choices[0].message.content
                    except Exception:
                        return str(resp)
            except Exception as e:
                last_err = e
            # Chat Completions fallback
            try:
                resp = self.client.chat.completions.create(model=model, messages=messages)
                return resp.choices[0].message.content
            except Exception as e2:
                last_err = e2
                continue
        raise RuntimeError(f"All model attempts failed. Last error: {last_err}")

    def _mock_translate(self, text: str, target: str) -> str:
        return f"[{target} translation of]: {text}"

    def _mock_answer(self, code: str) -> str:
        return {
            "en": "Mock thoughtful answer in English about responsibility and freedom.",
            "de": "Beispielhafte, nachdenkliche Antwort auf Deutsch über Verantwortung und Freiheit.",
            "fr": "Réponse réfléchie en français sur la responsabilité et la liberté.",
            "ja": "責任と自由についての思索的な日本語の回答です。",
            "ru": "Вдумчивый ответ на русском о ответственности и свободе."
        }.get(code, "Mock answer.")

    def _translate(self, text: str, target_lang_name: str) -> str:
        if self.dry_run:
            return self._mock_translate(text, target_lang_name)
        sys_prompt = SYSTEM_TRANSLATOR.format(
            target_lang_name=target_lang_name,
            translation_style=self.cfg["tone"]["translation_style"]
        )
        msgs = [{"role":"system","content":sys_prompt},{"role":"user","content":text}]
        return self._chat(msgs)

    def _ask_in_language(self, lang_code: str, question_translated: str) -> str:
        if self.dry_run:
            return self._mock_answer(lang_code)
        sys_prompt = SYSTEM_COUNSELOR.format(counselor_style=self.cfg["tone"]["counselor_style"])
        if lang_code == "de":
            user_prompt = USER_MAKE_GERMAN_PROMPT.format(question_de=question_translated)
        elif lang_code == "fr":
            user_prompt = USER_MAKE_FRENCH_PROMPT.format(question_fr=question_translated)
        elif lang_code == "ru":
            user_prompt = USER_MAKE_RUSSIAN_PROMPT.format(question_ru=question_translated)
        elif lang_code == "en":
            user_prompt = USER_MAKE_ENGLISH_PROMPT.format(question_en=question_translated)
        elif lang_code == "ja":
            user_prompt = USER_MAKE_JAPANESE_PROMPT.format(question_ja=question_translated)
        else:
            user_prompt = question_translated
        msgs = [{"role":"system","content":sys_prompt},{"role":"user","content":user_prompt}]
        return self._chat(msgs)

    def _back_to_english(self, text_in_lang: str) -> str:
        return self._translate(text_in_lang, "English")

    def run(self, question_en: str) -> Dict[str, Any]:
        active_langs = [l for l in self.cfg["languages"] if l.get("enabled")]
        blocks = []
        for l in active_langs:
            code, name = l["code"], l["name"]
            # translate EN→target (for English we still pass through to normalize phrasing)
            q_trans = self._translate(question_en, name)
            ans_lang = self._ask_in_language(code, q_trans)
            ans_en = ans_lang if code == "en" else self._back_to_english(ans_lang)
            blocks.append({
                "language": name,
                "code": code,
                "question_translated": q_trans,
                "answer_in_language": ans_lang,
                "answer_back_to_english": ans_en
            })

        # Synthesis (English)
        if self.dry_run:
            synthesis = "Synthesis: EN emphasizes clarity; DE emphasizes structure; FR highlights ambiguity/experience."
        else:
            msgs = [
                {"role":"system","content":"You are a concise philosophical editor."},
                {"role":"user","content":
                    "Compare these answers across languages (tone, concepts, and actionable insights). "
                    "Return a short English synthesis (<=150 words):\n\n" +
                    "\n\n".join(f"[{b['language']}] {b['answer_back_to_english']}" for b in blocks)
                }
            ]
            synthesis = self._chat(msgs)

        meta = {
            "timestamp": datetime.now(self.tz).isoformat(),
            "timezone": str(self.tz),
            "models_tried": self.models,
            "dry_run": self.dry_run
        }
        return {"question_en": question_en, "meta": meta, "blocks": blocks, "synthesis_en": synthesis}

    def save_journal(self, result: Dict[str, Any]) -> Path:
        out = self.output_dir / f"{self._now_stamp()}.md"
        md = []
        md.append("---")
        md.append(f"title: Philosophical Journal")
        md.append(f"created: {result['meta']['timestamp']}")
        md.append(f"timezone: {result['meta']['timezone']}")
        md.append(f"models_tried: {result['meta']['models_tried']}")
        md.append(f"dry_run: {result['meta']['dry_run']}")
        md.append("---\n")
        md.append("# Question (English)\n")
        md.append(result["question_en"] + "\n")
        for b in result["blocks"]:
            md.append(f"## {b['language']}")
            md.append(f"**Translated prompt:**\n\n{b['question_translated']}\n")
            md.append(f"**Answer in {b['language']}:**\n\n{b['answer_in_language']}\n")
            md.append(f"**Back-translation (English):**\n\n{b['answer_back_to_english']}\n")
        md.append("## Synthesis (English)\n")
        md.append(result["synthesis_en"] + "\n")
        out.write_text("\n".join(md), encoding="utf-8")
        return out
