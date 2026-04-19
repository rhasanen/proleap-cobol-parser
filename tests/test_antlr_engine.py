import pytest

from proleap_cobol_parser.parser.antlr_engine import CobolAntlrParserEngine, ParserNotGeneratedError


def test_engine_reports_unavailable_when_generated_modules_missing() -> None:
    engine = CobolAntlrParserEngine()
    assert engine.is_available() is False


def test_engine_parse_raises_if_generated_modules_missing() -> None:
    engine = CobolAntlrParserEngine()
    with pytest.raises(ParserNotGeneratedError):
        engine.parse("       IDENTIFICATION DIVISION.", ignore_syntax_errors=False)

