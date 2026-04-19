import re

from .constants import COMMENT_TAG, WS
from .line import CobolLine


class CobolInlineCommentEntriesNormalizer:
    _pattern = re.compile(r"\*>[^ ]")

    def process_line(self, line: CobolLine) -> CobolLine:
        if self._pattern.search(line.content_area) is None:
            return line
        new_content_area = line.content_area.replace(COMMENT_TAG, COMMENT_TAG + WS)
        return line.copy_with_indicator_and_content_area(line.indicator_area, new_content_area)

    def process_lines(self, lines: list[CobolLine]) -> list[CobolLine]:
        return [self.process_line(line) for line in lines]
