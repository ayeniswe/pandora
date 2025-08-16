"""Error handling and message naming"""
from .platforms.base import PlatformInfo


class ErrorMessage:
    def __init__(self, msg: str):
        self.msg = msg


class Error:
    """Error factory with static helpers for different error cases."""

    @staticmethod
    def PlatformUnsupported(info: PlatformInfo) -> ErrorMessage:
        return ErrorMessage(f"Unsupported platform: {info}")
