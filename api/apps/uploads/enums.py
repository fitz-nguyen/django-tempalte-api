from enum import Enum


class FileState(str, Enum):
    USED = "USED"
    DELETED = "DELETED"
    NEW = "NEW"
