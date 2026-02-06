# Twitter (X) AI Agent

Production-ready Python MVP for Crypto Twitter research and reply generation with human approval.

## Features
- X free-tier compatible ingestion with graceful simulation fallback.
- Manual tweet import by URL or ID.
- Keyword + hashtag filtering with relevance scoring.
- OpenAI-powered reply generation with 3 personas.
- CLI-based human approval queue (approve/reject/edit/regenerate).
- Reply evaluation with quality + engagement prediction.
- Weekly reporting with PDF + CSV + AI insights JSON.

## Personas
- `professional_analyst`
- `casual_degen`
- `neutral_researcher`

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py init
python main.py demo
```

## CLI Commands
```bash
python main.py init
python main.py collect --list-id <id> --count 10
python main.py import-tweet "https://x.com/user/status/1234567890"
python main.py generate --persona professional_analyst
python main.py queue --action show
python main.py queue --action approve --reply-id 1
python main.py queue --action edit --reply-id 1 --text "edited reply"
python main.py queue --action regenerate --reply-id 1 --persona casual_degen
python main.py evaluate
python main.py report
python main.py demo
```

## Notes on X Free Tier
- No search endpoint support used.
- No filtered stream support used.
- Auto-posting is not performed; approval queue is offline.
- List collection attempts API first and degrades to simulation on restrictions.
