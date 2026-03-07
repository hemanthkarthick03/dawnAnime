"pycache" Clean:

```bash
Get-ChildItem -Path . -Recurse -Directory -Include '__pycache__' | Remove-Item -Force -Recurse
```

Running Application:
```bash
uv run python -m app.main
```