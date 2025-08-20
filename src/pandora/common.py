"""Common shared enums"""
from enum import Enum

WRITE_TAG = "# Created by `pandora`"


class Status(Enum):
    Success = 0
    Failure = 1
    Warn = 2
