from pathlib import Path

import pytest

from proleap_cobol_parser.params import CobolParserParams, CobolSourceFormat
from proleap_cobol_parser.parser.antlr_engine import CobolParseResult, ParserNotGeneratedError
from proleap_cobol_parser.testing.ast_fixture_runner import CobolAstFixtureRunner


def test_fixture_runner_raises_without_generated_parser_modules() -> None:
    runner = CobolAstFixtureRunner()
    params = CobolParserParams(format=CobolSourceFormat.FIXED)
    repo_root = Path(__file__).resolve().parents[1]
    cobol_file = repo_root / "src/test/resources/io/proleap/cobol/ast/HelloWorld.cbl"
    with pytest.raises(ParserNotGeneratedError):
        runner.compare_file(cobol_file, params)


def test_fixture_runner_compares_normalized_tree_output(tmp_path: Path) -> None:
    class FakeTree:
        def toStringTree(self, recog):  # noqa: N802
            return "(startRule\\n (x ) )"

    class FakeEngine:
        def parse(self, preprocessed_code: str, ignore_syntax_errors: bool) -> CobolParseResult:
            return CobolParseResult(parse_tree=FakeTree(), syntax_errors=0, parser=object())

    cobol_file = tmp_path / "sample.cbl"
    tree_file = tmp_path / "sample.cbl.tree"
    cobol_file.write_text("000100 IDENTIFICATION DIVISION.", encoding="utf-8")
    tree_file.write_text("(startRule (x))", encoding="utf-8")

    runner = CobolAstFixtureRunner(parser_engine=FakeEngine())  # type: ignore[arg-type]
    params = CobolParserParams(format=CobolSourceFormat.FIXED)
    comparison = runner.compare_file(cobol_file, params, tree_file=tree_file)

    assert comparison.matched is True
