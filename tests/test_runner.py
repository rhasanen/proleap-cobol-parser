from pathlib import Path

from proleap_cobol_parser.params import CobolParserParams, CobolSourceFormat
from proleap_cobol_parser.parser.runner import CobolParserRunner


def test_runner_analyze_code_returns_preprocessed_output() -> None:
    runner = CobolParserRunner()
    params = CobolParserParams(format=CobolSourceFormat.FIXED)
    code = "000100 IDENTIFICATION DIVISION."
    result = runner.analyze_code(code, "Sample", params)
    assert result.compilation_unit_name == "Sample"
    assert "IDENTIFICATION DIVISION." in result.preprocessed_code


def test_runner_analyze_file_uses_stem_as_compilation_unit(tmp_path: Path) -> None:
    runner = CobolParserRunner()
    sample = tmp_path / "hello.cbl"
    sample.write_text("000100 IDENTIFICATION DIVISION.", encoding="utf-8")
    params = CobolParserParams(format=CobolSourceFormat.FIXED)
    result = runner.analyze_file(sample, params)
    assert result.compilation_unit_name == "Hello"
