from __future__ import annotations

from ..params import CobolParserParams
from .constants import (
    CHAR_ASTERISK,
    CHAR_D,
    CHAR_D_,
    CHAR_DOLLAR_SIGN,
    CHAR_MINUS,
    CHAR_SLASH,
    WS,
)
from .line import CobolLine
from .line_types import CobolLineType


class CobolLineReader:
    def determine_type(self, indicator_area: str) -> CobolLineType:
        if indicator_area in (CHAR_D, CHAR_D_):
            return CobolLineType.DEBUG
        if indicator_area == CHAR_MINUS:
            return CobolLineType.CONTINUATION
        if indicator_area in (CHAR_ASTERISK, CHAR_SLASH):
            return CobolLineType.COMMENT
        if indicator_area == CHAR_DOLLAR_SIGN:
            return CobolLineType.COMPILER_DIRECTIVE
        if indicator_area.strip() == "":
            return CobolLineType.NORMAL
        return CobolLineType.NORMAL

    def parse_line(self, line: str, line_number: int, params: CobolParserParams) -> CobolLine:
        matcher = params.format.pattern.match(line)
        if matcher is None:
            raise ValueError(
                f"Could not parse line {line_number + 1} in format {params.format.name}: {line}"
            )

        sequence_area = matcher.group(1) or ""
        indicator_area = matcher.group(2) or WS
        content_area_a = matcher.group(3) or ""
        content_area_b = matcher.group(4) or ""
        comment_area = matcher.group(5) or ""
        line_type = self.determine_type(indicator_area)
        return CobolLine.new(
            sequence_area=sequence_area,
            indicator_area=indicator_area,
            content_area_a=content_area_a,
            content_area_b=content_area_b,
            comment_area=comment_area,
            format=params.format,
            dialect=params.dialect,
            number=line_number,
            line_type=line_type,
        )

    def process_lines(self, code: str, params: CobolParserParams) -> list[CobolLine]:
        result: list[CobolLine] = []
        predecessor: CobolLine | None = None
        for i, line in enumerate(code.splitlines()):
            cobol_line = self.parse_line(line, i, params)
            cobol_line.set_predecessor(predecessor)
            result.append(cobol_line)
            predecessor = cobol_line
        return result
