# Contributing to VTT-Node

## Development Setup

```bash
git clone https://github.com/jahitchcock/Vtt-node.git
cd Vtt-node

cd vtt-ui
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
VTT_ENGINE=foundry API_SECRET=dev123 uvicorn main:app --reload
```

## Branching

| Branch | Purpose |
|---|---|
| `main` | Stable |
| `dev` | Active development |
| `feature/xxx` | PR into dev |
| `hotfix/xxx` | PR into main |

## Commit Style

```
type(scope): message
```
Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## PR Checklist

- [ ] All endpoints authed (except /health)
- [ ] No secrets in code
- [ ] Pydantic schema for new responses
- [ ] CHANGELOG.md updated
- [ ] Tested against both foundry + maptool modes
