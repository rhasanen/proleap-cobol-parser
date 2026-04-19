from pathlib import Path

from proleap_cobol_parser.params import CobolParserParams, CobolSourceFormat
from proleap_cobol_parser.parser.antlr_engine import CobolParseResult
from proleap_cobol_parser.parser.runner import CobolParserRunner


def test_runner_analyze_code_returns_preprocessed_output() -> None:
    runner = CobolParserRunner()
    params = CobolParserParams(format=CobolSourceFormat.FIXED)
    code = "000100 IDENTIFICATION DIVISION."
    result = runner.analyze_code(code, "Sample", params)
    assert result.compilation_unit_name == "Sample"
    assert "IDENTIFICATION DIVISION." in result.preprocessed_code
    assert result.parse_tree is None


def test_runner_analyze_file_uses_stem_as_compilation_unit(tmp_path: Path) -> None:
    runner = CobolParserRunner()
    sample = tmp_path / "hello.cbl"
    sample.write_text("000100 IDENTIFICATION DIVISION.", encoding="utf-8")
    params = CobolParserParams(format=CobolSourceFormat.FIXED)
    result = runner.analyze_file(sample, params)
    assert result.compilation_unit_name == "Hello"


def test_runner_uses_parser_engine_when_provided() -> None:
    class DummyParserEngine:
        def parse(self, preprocessed_code: str, ignore_syntax_errors: bool) -> CobolParseResult:
            return CobolParseResult(parse_tree={"ok": True}, syntax_errors=0)

    runner = CobolParserRunner(parser_engine=DummyParserEngine())  # type: ignore[arg-type]
    params = CobolParserParams(format=CobolSourceFormat.FIXED)
    result = runner.analyze_code("000100 IDENTIFICATION DIVISION.", "Sample", params)
    assert result.parse_tree == {"ok": True}
    assert result.syntax_errors == 0


def test_runner_analyze_file_uses_parser_engine_when_provided(tmp_path: Path) -> None:
    class DummyParserEngine:
        def parse(self, preprocessed_code: str, ignore_syntax_errors: bool) -> CobolParseResult:
            return CobolParseResult(parse_tree="tree", syntax_errors=0)

    sample = tmp_path / "hello.cbl"
    sample.write_text("000100 IDENTIFICATION DIVISION.", encoding="utf-8")
    runner = CobolParserRunner(parser_engine=DummyParserEngine())  # type: ignore[arg-type]
    params = CobolParserParams(format=CobolSourceFormat.FIXED)
    result = runner.analyze_file(sample, params)
    assert result.parse_tree == "tree"
