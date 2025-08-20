"""Error handling and message naming"""
from pathlib import Path

from .platforms.base import PlatformInfo


class ErrorMessage(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg


class Error:
    """Error factory with static helpers for different error cases."""

    @staticmethod
    def PlatformUnsupported(info: PlatformInfo) -> ErrorMessage:
        return ErrorMessage(f"Unsupported platform: {info}")

    @staticmethod
    def ConfigNotFound(config: str | Path) -> ErrorMessage:
        return ErrorMessage(f"config file not found: {config}")

    @staticmethod
    def InstallFailure(pkg: str) -> ErrorMessage:
        return ErrorMessage(f"failed to install: {pkg}")
