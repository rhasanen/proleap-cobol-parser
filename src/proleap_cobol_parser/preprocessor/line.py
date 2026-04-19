from __future__ import annotations

from dataclasses import dataclass

from ..params import CobolDialect, CobolSourceFormat
from .constants import WS
from .line_types import CobolLineType


@dataclass
class CobolLine:
    sequence_area: str
    sequence_area_original: str
    indicator_area: str
    indicator_area_original: str
    content_area_a: str
    content_area_a_original: str
    content_area_b: str
    content_area_b_original: str
    comment_area: str
    comment_area_original: str
    format: CobolSourceFormat
    dialect: CobolDialect
    number: int
    type: CobolLineType
    predecessor: "CobolLine | None" = None
    successor: "CobolLine | None" = None

    @property
    def content_area(self) -> str:
        return f"{self.content_area_a}{self.content_area_b}"

    @property
    def content_area_original(self) -> str:
        return f"{self.content_area_a_original}{self.content_area_b_original}"

    @property
    def blank_sequence_area(self) -> str:
        return "" if self.format is CobolSourceFormat.TANDEM else WS * 6

    def set_predecessor(self, predecessor: "CobolLine | None") -> None:
        self.predecessor = predecessor
        if predecessor is not None:
            predecessor.successor = self

    def serialize(self) -> str:
        return (
            self.sequence_area
            + self.indicator_area
            + self.content_area_a
            + self.content_area_b
            + self.comment_area
        )

    @staticmethod
    def new(
        sequence_area: str,
        indicator_area: str,
        content_area_a: str,
        content_area_b: str,
        comment_area: str,
        format: CobolSourceFormat,
        dialect: CobolDialect,
        number: int,
        line_type: CobolLineType,
    ) -> "CobolLine":
        return CobolLine(
            sequence_area=sequence_area,
            sequence_area_original=sequence_area,
            indicator_area=indicator_area,
            indicator_area_original=indicator_area,
            content_area_a=content_area_a,
            content_area_a_original=content_area_a,
            content_area_b=content_area_b,
            content_area_b_original=content_area_b,
            comment_area=comment_area,
            comment_area_original=comment_area,
            format=format,
            dialect=dialect,
            number=number,
            type=line_type,
        )

    def copy_with_indicator_and_content_area(
        self, indicator_area: str, content_area: str
    ) -> "CobolLine":
        content_area_a = content_area[:4]
        content_area_b = content_area[4:] if len(content_area) > 4 else ""
        return CobolLine(
            sequence_area=self.sequence_area,
            sequence_area_original=self.sequence_area_original,
            indicator_area=indicator_area,
            indicator_area_original=self.indicator_area_original,
            content_area_a=content_area_a,
            content_area_a_original=self.content_area_a_original,
            content_area_b=content_area_b,
            content_area_b_original=self.content_area_b_original,
            comment_area=self.comment_area,
            comment_area_original=self.comment_area_original,
            format=self.format,
            dialect=self.dialect,
            number=self.number,
            type=self.type,
            predecessor=self.predecessor,
            successor=self.successor,
        )

    def copy_with_indicator_area(self, indicator_area: str) -> "CobolLine":
        return CobolLine(
            sequence_area=self.sequence_area,
            sequence_area_original=self.sequence_area_original,
            indicator_area=indicator_area,
            indicator_area_original=self.indicator_area_original,
            content_area_a=self.content_area_a,
            content_area_a_original=self.content_area_a_original,
            content_area_b=self.content_area_b,
            content_area_b_original=self.content_area_b_original,
            comment_area=self.comment_area,
            comment_area_original=self.comment_area_original,
            format=self.format,
            dialect=self.dialect,
            number=self.number,
            type=self.type,
            predecessor=self.predecessor,
            successor=self.successor,
        )
