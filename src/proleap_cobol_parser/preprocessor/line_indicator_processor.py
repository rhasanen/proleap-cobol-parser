import re

from .constants import COMMENT_TAG, WS
from .line import CobolLine
from .line_types import CobolLineType


class CobolLineIndicatorProcessor:
    _empty = ""

    def _trim_leading_ws(self, value: str) -> str:
        return re.sub(r"^\s+", self._empty, value)

    def _trim_trailing_ws(self, value: str) -> str:
        return re.sub(r"\s+$", self._empty, value)

    def _repair_trailing_comma(self, value: str) -> str:
        if value and value[-1] in {",", ";"}:
            return value + WS
        return value

    def _right_trim_content_area(self, value: str) -> str:
        return self._repair_trailing_comma(self._trim_trailing_ws(value))

    def _remove_string_literals(self, value: str) -> str:
        result: list[str] = []
        i = 0
        quote_char: str | None = None

        while i < len(value):
            ch = value[i]

            if quote_char is None:
                if ch in {"'", '"'}:
                    quote_char = ch
                    i += 1
                    continue
                result.append(ch)
                i += 1
                continue

            if ch == quote_char:
                if i + 1 < len(value) and value[i + 1] == quote_char:
                    i += 2
                    continue
                quote_char = None
                i += 1
                continue

            i += 1

        return "".join(result)

    def _is_ending_with_open_literal(self, line: CobolLine) -> bool:
        no_literals = self._remove_string_literals(line.content_area_original)
        return '"' in no_literals or "'" in no_literals

    def _is_next_line_continuation(self, line: CobolLine) -> bool:
        return line.successor is not None and line.successor.type is CobolLineType.CONTINUATION

    def _conditional_right_trim_content_area(self, line: CobolLine) -> str:
        if not self._is_next_line_continuation(line):
            return self._right_trim_content_area(line.content_area)
        if not self._is_ending_with_open_literal(line):
            return self._right_trim_content_area(line.content_area)
        return line.content_area

    def process_line(self, line: CobolLine) -> CobolLine:
        content = self._conditional_right_trim_content_area(line)
        if line.type is CobolLineType.DEBUG:
            return line.copy_with_indicator_and_content_area(WS, content)
        if line.type is CobolLineType.CONTINUATION:
            if not content:
                return line.copy_with_indicator_and_content_area(WS, self._empty)
            predecessor = line.predecessor
            if predecessor is not None and (
                predecessor.content_area_original.endswith('"')
                or predecessor.content_area_original.endswith("'")
            ):
                trimmed = self._trim_leading_ws(content)
                if trimmed.startswith('"') or trimmed.startswith("'"):
                    return line.copy_with_indicator_and_content_area(WS, trimmed[1:])
                return line.copy_with_indicator_and_content_area(WS, self._trim_leading_ws(content))
            if predecessor is not None and self._is_ending_with_open_literal(predecessor):
                trimmed = self._trim_leading_ws(content)
                if trimmed.startswith('"') or trimmed.startswith("'"):
                    return line.copy_with_indicator_and_content_area(WS, trimmed[1:])
                return line.copy_with_indicator_and_content_area(WS, content)
            if predecessor is not None and (
                predecessor.content_area.endswith('"') or predecessor.content_area.endswith("'")
            ):
                return line.copy_with_indicator_and_content_area(WS, WS + self._trim_leading_ws(content))
            return line.copy_with_indicator_and_content_area(WS, self._trim_leading_ws(content))
        if line.type is CobolLineType.COMMENT:
            return line.copy_with_indicator_and_content_area(COMMENT_TAG + WS, content)
        if line.type is CobolLineType.COMPILER_DIRECTIVE:
            return line.copy_with_indicator_and_content_area(WS, self._empty)
        return line.copy_with_indicator_and_content_area(WS, content)

    def process_lines(self, lines: list[CobolLine]) -> list[CobolLine]:
        return [self.process_line(line) for line in lines]
