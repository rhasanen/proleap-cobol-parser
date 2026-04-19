from dataclasses import dataclass, field
from enum import Enum
import re
from pathlib import Path


_INDICATOR_FIELD = r"([ABCdD$\t\-/*# ])"


class CobolSourceFormat(Enum):
    FIXED = (rf"(.{{0,6}})(?:{_INDICATOR_FIELD}(.{{0,4}})(.{{0,61}})(.*))?", True)
    TANDEM = (rf"()(?:{_INDICATOR_FIELD}(.{{0,4}})(.*)())?", False)
    VARIABLE = (rf"(.{{0,6}})(?:{_INDICATOR_FIELD}(.{{0,4}})(.*)())?", True)

    def __init__(self, regex: str, comment_entry_multi_line: bool):
        self.regex = regex
        self.comment_entry_multi_line = comment_entry_multi_line
        self.pattern = re.compile(regex)


class CobolDialect(Enum):
    IBM = "IBM"
    OSVS = "OSVS"


@dataclass
class CobolParserParams:
    format: CobolSourceFormat = CobolSourceFormat.FIXED
    dialect: CobolDialect = CobolDialect.IBM
    charset: str = "utf-8"
    copybook_directories: list[Path] = field(default_factory=list)
    copybook_extensions: list[str] = field(default_factory=list)
    copybook_files: list[Path] = field(default_factory=list)
    ignore_syntax_errors: bool = False
