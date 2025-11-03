# local-file-mcp-server
A simple mcp server to serve local files


## Development getting started

This project uses `uv`, a better and faster python package manager.
Install it according to this [documentation](https://docs.astral.sh/uv/getting-started/installation).

### Prepare dev environment
Create venv and install all dependencies defined in `pyproject.toml`:
```
uv sync --all-groups
```

### Run server locally
```
uv run main.py
```