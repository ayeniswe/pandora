# pandora

Out-of-box dev env for any machine—online or offline. Skip setup headaches with prebundled tools, deps, and services. Ideal for secure/offline teams, fast onboarding, and consistent, reproducible builds across projects

## Development

This project is managed with [Poetry](https://python-poetry.org/).
> Note: `pip install poetry poetry-plugin-shell` if you have not already

### 1. Bootstrap the environment
```bash
# (optional) keep venv local to project
poetry config virtualenvs.in-project true

poetry install && poetry shell
```

### 2. Run the app
```bash
poetry run pandora 
```

## Packaging

Executables can be produced with [PyInstaller](https://pyinstaller.org):
> Note: `pip install pyinstaller` if you have not already

```bash
scripts/package.sh
```

The resulting binary in `dist/` can be executed on systems without Python.
