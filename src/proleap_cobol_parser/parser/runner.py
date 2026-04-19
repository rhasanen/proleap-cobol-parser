from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..params import CobolParserParams, CobolSourceFormat
from ..preprocessor.preprocessor import CobolPreprocessor
from .antlr_engine import CobolAntlrParserEngine, ParserNotGeneratedError


@dataclass
class CobolAnalysisResult:
    compilation_unit_name: str
    preprocessed_code: str
    parse_tree: object | None = None
    syntax_errors: int | None = None
    asg: object | None = None


class CobolParserRunner:
    def __init__(self, parser_engine: CobolAntlrParserEngine | None = None) -> None:
        self._preprocessor = CobolPreprocessor()
        self._parser_engine = parser_engine or CobolAntlrParserEngine()

    def analyze_code(
        self, cobol_code: str, compilation_unit_name: str, params: CobolParserParams
    ) -> CobolAnalysisResult:
        preprocessed_code = self._preprocessor.process_code(cobol_code, params)
        parse_tree = None
        syntax_errors = None

        try:
            parse_result = self._parser_engine.parse(preprocessed_code, params.ignore_syntax_errors)
            parse_tree = parse_result.parse_tree
            syntax_errors = parse_result.syntax_errors
        except ParserNotGeneratedError:
            pass

        return CobolAnalysisResult(
            compilation_unit_name=compilation_unit_name,
            preprocessed_code=preprocessed_code,
            parse_tree=parse_tree,
            syntax_errors=syntax_errors,
            asg=None,
        )

    def analyze_file(self, cobol_file: Path, params: CobolParserParams) -> CobolAnalysisResult:
        preprocessed_code = self._preprocessor.process_file(cobol_file, params)
        return CobolAnalysisResult(
            compilation_unit_name=cobol_file.stem.capitalize(),
            preprocessed_code=preprocessed_code,
            parse_tree=None,
            asg=None,
        )

    def analyze_file_with_format(
        self, cobol_file: Path, source_format: CobolSourceFormat
    ) -> CobolAnalysisResult:
        params = CobolParserParams(format=source_format, copybook_directories=[cobol_file.parent])
        return self.analyze_file(cobol_file, params)
