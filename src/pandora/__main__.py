"""Entry point for the pandora package."""

from __future__ import annotations

from .platforms import detect_platform
from .offline import env

def main() -> None:
    """Run the main entry point."""

    info = detect_platform()
    print(
        f"Running on {info.os.value} "
        f"{info.subtype or 'unknown'} "
        f"({info.arch.value})",
    )
    prefs = {"TEST": "12345", "TEST2": "123"}
    # prefs = {"TEST": "12345", "TEST2": "A" * 40000}
    env.setup_vars(info, prefs)

if __name__ == "__main__":
    main()
