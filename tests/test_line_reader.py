from proleap_cobol_parser.params import CobolParserParams, CobolSourceFormat
from proleap_cobol_parser.preprocessor.line_reader import CobolLineReader
from proleap_cobol_parser.preprocessor.line_types import CobolLineType


def test_parse_fixed_line() -> None:
    reader = CobolLineReader()
    params = CobolParserParams(format=CobolSourceFormat.FIXED)
    line = reader.parse_line("000100 IDENTIFICATION DIVISION.", 0, params)
    assert line.sequence_area == "000100"
    assert line.indicator_area == " "
    assert line.type is CobolLineType.NORMAL


def test_parse_tandem_comment_line() -> None:
    reader = CobolLineReader()
    params = CobolParserParams(format=CobolSourceFormat.TANDEM)
    line = reader.parse_line("* comment", 0, params)
    assert line.type is CobolLineType.COMMENT
