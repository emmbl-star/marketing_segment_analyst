# marketing_segment_analyst

Portfolio project: automating the analysis and optimization of marketing segments.

## Status

Early scaffold. The Streamlit app is currently a placeholder demo.

## Structure

- `app.py` — Streamlit entry point
- `agents/` — Claude-based agents (planned)
- `gcp/` — Google Cloud integration (planned)
- `utils/` — shared helpers (planned)
- `raw_data/` — local datasets (git-ignored)

## Getting started

```bash
cp .env.example .env   # then fill in ANTHROPIC_API_KEY
make install_requirements
make streamlit
```

The app is served on http://localhost:8501.
