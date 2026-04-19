from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..params import CobolParserParams
from ..parser.antlr_engine import CobolAntlrParserEngine
from ..preprocessor.preprocessor import CobolPreprocessor
from .ast_compare import normalize_tree


@dataclass
class CobolAstFixtureComparison:
    matched: bool
    expected_tree_file: Path
    normalized_expected_tree: str
    normalized_actual_tree: str


class CobolAstFixtureRunner:
    TREE_SUFFIX = ".tree"

    def __init__(self, parser_engine: CobolAntlrParserEngine | None = None) -> None:
        self._preprocessor = CobolPreprocessor()
        self._parser_engine = parser_engine or CobolAntlrParserEngine()

    def compare_file(
        self,
        cobol_file: Path,
        params: CobolParserParams,
        tree_file: Path | None = None,
    ) -> CobolAstFixtureComparison:
        expected_tree_file = tree_file or Path(f"{cobol_file}{self.TREE_SUFFIX}")
        preprocessed_code = self._preprocessor.process_file(cobol_file, params)
        parse_result = self._parser_engine.parse(preprocessed_code, params.ignore_syntax_errors)

        parser = parse_result.parser
        parse_tree = parse_result.parse_tree
        if parser is None:
            raise RuntimeError("Parser metadata is missing in parse result.")

        actual_tree = parse_tree.toStringTree(recog=parser)
        expected_tree = expected_tree_file.read_text(encoding=params.charset)

        normalized_actual_tree = normalize_tree(actual_tree)
        normalized_expected_tree = normalize_tree(expected_tree)
        return CobolAstFixtureComparison(
            matched=normalized_actual_tree == normalized_expected_tree,
            expected_tree_file=expected_tree_file,
            normalized_expected_tree=normalized_expected_tree,
            normalized_actual_tree=normalized_actual_tree,
        )

