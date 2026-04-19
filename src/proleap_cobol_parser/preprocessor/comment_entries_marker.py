import re

from ..params import CobolDialect
from .constants import COMMENT_ENTRY_TAG, WS
from .line import CobolLine
from .line_types import CobolLineType


class CobolCommentEntriesMarker:
    _triggers_end = [
        "PROGRAM-ID.",
        "AUTHOR.",
        "INSTALLATION.",
        "DATE-WRITTEN.",
        "DATE-COMPILED.",
        "SECURITY.",
        "ENVIRONMENT",
        "DATA.",
        "PROCEDURE.",
    ]
    _triggers_start = [
        "AUTHOR.",
        "INSTALLATION.",
        "DATE-WRITTEN.",
        "DATE-COMPILED.",
        "SECURITY.",
        "REMARKS.",
    ]

    def __init__(self) -> None:
        trigger_expr = "|".join(self._triggers_start)
        self._trigger_pattern = re.compile(rf"([ \t]*)({trigger_expr})(.+)", re.IGNORECASE)
        self._found_trigger_in_prev_line = False
        self._in_comment_entry = False

    def _starts_with_trigger(self, line: CobolLine, triggers: list[str]) -> bool:
        content = line.content_area.upper().strip()
        return any(content.startswith(trigger) for trigger in triggers)

    def _is_in_osvs_comment_entry(self, line: CobolLine) -> bool:
        return line.dialect is CobolDialect.OSVS and not self._starts_with_trigger(line, self._triggers_end)

    def _escape_comment_entry(self, line: CobolLine) -> CobolLine:
        match = self._trigger_pattern.match(line.content_area)
        if match is None:
            return line
        whitespace, trigger, comment_entry = match.groups()
        new_content_area = f"{whitespace}{trigger}{WS}{COMMENT_ENTRY_TAG}{comment_entry}"
        return line.copy_with_indicator_and_content_area(line.indicator_area, new_content_area)

    def process_line(self, line: CobolLine) -> CobolLine:
        if not line.format.comment_entry_multi_line:
            if self._starts_with_trigger(line, self._triggers_start):
                return self._escape_comment_entry(line)
            return line

        found_trigger_current = self._starts_with_trigger(line, self._triggers_start)
        result = line
        if found_trigger_current:
            result = self._escape_comment_entry(line)
        elif self._found_trigger_in_prev_line or self._in_comment_entry:
            is_content_area_a_empty = line.content_area_a.strip() == ""
            is_in_osvs_comment_entry = self._is_in_osvs_comment_entry(line)
            self._in_comment_entry = (
                line.type is CobolLineType.COMMENT or is_content_area_a_empty or is_in_osvs_comment_entry
            )
            if self._in_comment_entry:
                result = line.copy_with_indicator_area(COMMENT_ENTRY_TAG + WS)

        self._found_trigger_in_prev_line = found_trigger_current
        return result

    def process_lines(self, lines: list[CobolLine]) -> list[CobolLine]:
        result: list[CobolLine] = []
        for line in lines:
            result.append(self.process_line(line))
        return result
