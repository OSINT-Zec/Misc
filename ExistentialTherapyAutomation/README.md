# Existential Therapy Automation — Multi‑Language (EN+DE+FR) + optional JA/RU via OpenAI API

Ask a philosophical question **once** and automatically:
- translate it to **German** and **French** (English included by default),
- get **philosophical answers** in EN/DE/FR (JA/RU optional),
- translate non‑English answers **back into English**,
- compile a clean **English journal** for later human feedback.

Defaults to model **gpt-5** (as requested) with automatic fallbacks.

---

## Features
- **Languages**: English (`en`), German (`de`), French (`fr`) enabled by default.
- **Optional**: Japanese (`ja`) and Russian (`ru`) — toggle in `config.yaml` or per-run flags.
- **Prompts** tuned for *philosophical counseling / existential reflection*.
- **OpenAI API** with model fallback.
- **Dry‑run** mode for offline testing.
- Outputs Markdown in `journal/` with metadata.

---

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # add OPENAI_API_KEY
```

Optional: edit `config.yaml` to tweak languages or models.

---

## Usage

```bash
python run_pipeline.py "What does it really mean to take responsibility for my choices?"
```

Read from file:
```bash
python run_pipeline.py --file sample_question.txt
```

Enable **Japanese** (one-time toggle):
```bash
python run_pipeline.py --with-ja "Is radical freedom possible without loneliness?"
```

Enable **Russian** (one-time toggle):
```bash
python run_pipeline.py --with-ru "How should I relate to suffering without romanticizing it?"
```

**Dry run (no API calls):**
```bash
python run_pipeline.py --dry-run "Test pipeline without calling the API."
```

Journal saved to `journal/YYYY-MM-DD_HHMMSS_kst.md`.

---

## Models & Fallbacks
- Primary: **gpt-5**
- Fallbacks: `gpt-4.1`, `gpt-4o-mini`

Adjust in `config.yaml` if needed.

---

## Privacy
All journals are local Markdown files. Share selectively.
