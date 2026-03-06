"pycache" Clean:

```bash
Get-ChildItem -Path . -Recurse -Directory -Include '__pycache__' | Remove-Item -Force -Recurse
```

```python
    
```