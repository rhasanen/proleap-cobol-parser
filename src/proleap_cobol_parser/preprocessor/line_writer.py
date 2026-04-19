from .constants import NEWLINE
from .line import CobolLine
from .line_types import CobolLineType


class CobolLineWriter:
    def serialize(self, lines: list[CobolLine]) -> str:
        chunks: list[str] = []
        for line in lines:
            if line.type is not CobolLineType.CONTINUATION:
                if line.number > 0:
                    chunks.append(NEWLINE)
                chunks.append(line.blank_sequence_area)
                chunks.append(line.indicator_area)
            chunks.append(line.content_area)
        return "".join(chunks)
