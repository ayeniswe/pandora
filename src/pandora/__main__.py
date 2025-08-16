"""Entry point for the pandora package."""

from __future__ import annotations

from .platforms import detect_platform


def main() -> None:
    """Run the main entry point."""

    info = detect_platform()
    print(
        f"Running on {info.os.value} "
        f"{info.subtype or 'unknown'} "
        f"({info.arch.value})",
    )


if __name__ == "__main__":  # pragma: no cover
    main()
