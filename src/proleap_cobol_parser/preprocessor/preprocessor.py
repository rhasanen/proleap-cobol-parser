from pathlib import Path

from ..params import CobolParserParams
from .comment_entries_marker import CobolCommentEntriesMarker
from .inline_comment_entries_normalizer import CobolInlineCommentEntriesNormalizer
from .line_indicator_processor import CobolLineIndicatorProcessor
from .line_reader import CobolLineReader
from .line_writer import CobolLineWriter


class CobolPreprocessor:
    def __init__(self) -> None:
        self._line_reader = CobolLineReader()
        self._line_indicator_processor = CobolLineIndicatorProcessor()
        self._inline_normalizer = CobolInlineCommentEntriesNormalizer()
        self._comment_marker = CobolCommentEntriesMarker()
        self._line_writer = CobolLineWriter()

    def process_code(self, cobol_code: str, params: CobolParserParams) -> str:
        lines = self._line_reader.process_lines(cobol_code, params)
        lines = self._line_indicator_processor.process_lines(lines)
        lines = self._inline_normalizer.process_lines(lines)
        lines = self._comment_marker.process_lines(lines)
        return self._line_writer.serialize(lines)

    def process_file(self, cobol_file: Path, params: CobolParserParams) -> str:
        return self.process_code(cobol_file.read_text(encoding=params.charset), params)
