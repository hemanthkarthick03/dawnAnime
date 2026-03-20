"pycache" Clean:

```bash
Get-ChildItem -Path . -Recurse -Directory -Include '__pycache__' | Remove-Item -Force -Recurse
```

Running Application:
```bash
uv run python -m app.main

uvicorn app.main:app --host 127.0.0.1 --port 8055 --reload
```