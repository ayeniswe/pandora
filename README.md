# pandora

Out-of-box dev env for any machine—online or offline. Skip setup headaches with prebundled tools, deps, and services. Ideal for secure/offline teams, fast onboarding, and consistent, reproducible builds across projects

## Development

This repository uses [pre-commit](https://pre-commit.com) with Ruff, mypy and codespell to
ensure code quality. Install the tooling and run the checks:

```bash
pip install pre-commit
pre-commit run --files <files>
```

## Packaging

Executables can be produced with [PyInstaller](https://pyinstaller.org):

```bash
scripts/package.sh
```

The resulting binary in `dist/` can be executed on systems without Python.
