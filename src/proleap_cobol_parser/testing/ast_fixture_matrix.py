from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ..params import CobolParserParams, CobolSourceFormat
from ..parser.antlr_engine import CobolAntlrParserEngine, ParserNotGeneratedError
from .ast_fixture_runner import CobolAstFixtureComparison, CobolAstFixtureRunner


@dataclass(frozen=True)
class CobolAstFixtureCase:
    cobol_file: Path
    tree_file: Path
    source_format: CobolSourceFormat


@dataclass
class CobolAstFixtureMatrixResult:
    comparisons: list[tuple[CobolAstFixtureCase, CobolAstFixtureComparison]]

    @property
    def total(self) -> int:
        return len(self.comparisons)

    @property
    def matched(self) -> int:
        return sum(1 for _, comparison in self.comparisons if comparison.matched)

    @property
    def mismatched(self) -> int:
        return self.total - self.matched


class CobolAstFixtureMatrixRunner:
    def __init__(
        self,
        parser_engine: CobolAntlrParserEngine | None = None,
        fixture_runner: CobolAstFixtureRunner | None = None,
        ast_fixture_root: Path | None = None,
    ) -> None:
        self._parser_engine = parser_engine or CobolAntlrParserEngine()
        self._fixture_runner = fixture_runner or CobolAstFixtureRunner(parser_engine=self._parser_engine)
        self._ast_fixture_root = ast_fixture_root or (
            Path(__file__).resolve().parents[3] / "src/test/resources/io/proleap/cobol/ast"
        )

    def is_parser_available(self) -> bool:
        is_available = getattr(self._parser_engine, "is_available", None)
        if callable(is_available):
            return bool(is_available())
        return True

    def discover_cases(
        self,
        max_cases: int | None = None,
        name_contains: str | None = None,
        formats: set[CobolSourceFormat] | None = None,
    ) -> list[CobolAstFixtureCase]:
        cases: list[CobolAstFixtureCase] = []
        tree_files = sorted(self._ast_fixture_root.rglob("*.cbl.tree"))

        for tree_file in tree_files:
            cobol_file = tree_file.with_suffix("")
            if not cobol_file.exists():
                continue

            if name_contains is not None and name_contains not in cobol_file.name:
                continue

            source_format = self._infer_source_format(cobol_file)
            if formats is not None and source_format not in formats:
                continue

            cases.append(
                CobolAstFixtureCase(
                    cobol_file=cobol_file,
                    tree_file=tree_file,
                    source_format=source_format,
                )
            )

            if max_cases is not None and len(cases) >= max_cases:
                break

        return cases

    def run(
        self,
        max_cases: int | None = None,
        name_contains: str | None = None,
        formats: set[CobolSourceFormat] | None = None,
        params_factory: Callable[[CobolAstFixtureCase], CobolParserParams] | None = None,
    ) -> CobolAstFixtureMatrixResult:
        if not self.is_parser_available():
            raise ParserNotGeneratedError(
                "Generated ANTLR parser modules are missing. "
                "Run 'python scripts/generate_python_antlr.py' from the repository root."
            )

        cases = self.discover_cases(max_cases=max_cases, name_contains=name_contains, formats=formats)
        comparisons: list[tuple[CobolAstFixtureCase, CobolAstFixtureComparison]] = []
        for case in cases:
            params = (
                params_factory(case)
                if params_factory is not None
                else CobolParserParams(
                    format=case.source_format,
                    copybook_directories=[case.cobol_file.parent],
                )
            )
            comparisons.append(
                (
                    case,
                    self._fixture_runner.compare_file(
                        cobol_file=case.cobol_file,
                        params=params,
                        tree_file=case.tree_file,
                    ),
                )
            )

        return CobolAstFixtureMatrixResult(comparisons=comparisons)

    def _infer_source_format(self, cobol_file: Path) -> CobolSourceFormat:
        parent_name = cobol_file.parent.name.lower()
        if parent_name == "fixed":
            return CobolSourceFormat.FIXED
        if parent_name == "tandem":
            return CobolSourceFormat.TANDEM
        if parent_name == "variable":
            return CobolSourceFormat.VARIABLE
        return CobolSourceFormat.FIXED
