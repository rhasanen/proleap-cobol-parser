from proleap_cobol_parser.params import CobolParserParams, CobolSourceFormat
from proleap_cobol_parser.preprocessor.preprocessor import CobolPreprocessor


def test_preprocessor_marks_comment_line() -> None:
    params = CobolParserParams(format=CobolSourceFormat.FIXED)
    preprocessor = CobolPreprocessor()
    code = "000100*COMMENT LINE"
    result = preprocessor.process_code(code, params)
    assert "*> COMMENT LINE" in result


def test_preprocessor_continuation_trims_leading_ws() -> None:
    params = CobolParserParams(format=CobolSourceFormat.FIXED)
    preprocessor = CobolPreprocessor()
    code = "000100  DISPLAY 'A'\n000200-   'B'"
    result = preprocessor.process_code(code, params)
    assert "'A''B'" in result
