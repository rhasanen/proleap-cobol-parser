from pathlib import Path

import pytest

from proleap_cobol_parser.params import CobolParserParams, CobolSourceFormat
from proleap_cobol_parser.parser.antlr_engine import ParserNotGeneratedError
from proleap_cobol_parser.testing.ast_fixture_runner import CobolAstFixtureComparison
from proleap_cobol_parser.testing.ast_fixture_matrix import CobolAstFixtureMatrixRunner


def _create_fixture_case(root: Path, format_name: str, base_name: str) -> None:
    folder = root / format_name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{base_name}.cbl").write_text("000100 IDENTIFICATION DIVISION.", encoding="utf-8")
    (folder / f"{base_name}.cbl.tree").write_text("(startRule (x))", encoding="utf-8")


def test_matrix_runner_discover_cases_infers_source_format(tmp_path: Path) -> None:
    _create_fixture_case(tmp_path, "fixed", "Alpha")
    _create_fixture_case(tmp_path, "tandem", "Beta")
    _create_fixture_case(tmp_path, "variable", "Gamma")

    runner = CobolAstFixtureMatrixRunner(ast_fixture_root=tmp_path)
    cases = runner.discover_cases()

    assert len(cases) == 3
    formats = {case.cobol_file.stem: case.source_format for case in cases}
    assert formats["Alpha"] == CobolSourceFormat.FIXED
    assert formats["Beta"] == CobolSourceFormat.TANDEM
    assert formats["Gamma"] == CobolSourceFormat.VARIABLE


def test_matrix_runner_discover_cases_respects_filters(tmp_path: Path) -> None:
    _create_fixture_case(tmp_path, "fixed", "Alpha")
    _create_fixture_case(tmp_path, "fixed", "Alpine")
    _create_fixture_case(tmp_path, "variable", "Beta")

    runner = CobolAstFixtureMatrixRunner(ast_fixture_root=tmp_path)
    cases = runner.discover_cases(
        max_cases=1,
        name_contains="Al",
        formats={CobolSourceFormat.FIXED},
    )

    assert len(cases) == 1
    assert "Al" in cases[0].cobol_file.name
    assert cases[0].source_format == CobolSourceFormat.FIXED


def test_matrix_runner_run_aggregates_match_counts(tmp_path: Path) -> None:
    _create_fixture_case(tmp_path, "fixed", "Match")
    _create_fixture_case(tmp_path, "fixed", "Mismatch")

    class StubParserEngine:
        def is_available(self) -> bool:
            return True

    class StubFixtureRunner:
        def compare_file(self, cobol_file: Path, params: CobolParserParams, tree_file: Path) -> CobolAstFixtureComparison:
            matched = "Mismatch" not in cobol_file.name
            return CobolAstFixtureComparison(
                matched=matched,
                expected_tree_file=tree_file,
                normalized_expected_tree="expected",
                normalized_actual_tree="actual",
            )

    runner = CobolAstFixtureMatrixRunner(
        parser_engine=StubParserEngine(),  # type: ignore[arg-type]
        fixture_runner=StubFixtureRunner(),  # type: ignore[arg-type]
        ast_fixture_root=tmp_path,
    )
    result = runner.run()

    assert result.total == 2
    assert result.matched == 1
    assert result.mismatched == 1


def test_matrix_runner_run_raises_when_parser_not_available(tmp_path: Path) -> None:
    _create_fixture_case(tmp_path, "fixed", "Alpha")

    class StubUnavailableParserEngine:
        def is_available(self) -> bool:
            return False

    runner = CobolAstFixtureMatrixRunner(
        parser_engine=StubUnavailableParserEngine(),  # type: ignore[arg-type]
        ast_fixture_root=tmp_path,
    )

    with pytest.raises(ParserNotGeneratedError):
        runner.run()
