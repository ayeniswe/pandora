"""Entry point for the pandora package."""

from __future__ import annotations

from .offline import env
from .platforms import detect_platform


def main() -> None:
    """Run the main entry point."""

    info = detect_platform()
    print(
        f"Running on {info.os.value} " f"{info.subtype or 'unknown'} " f"({info.arch.value})",
    )

    # TODO read in user supplied env var sheet
    env.setup_vars(info, {})


if __name__ == "__main__":
    main()
