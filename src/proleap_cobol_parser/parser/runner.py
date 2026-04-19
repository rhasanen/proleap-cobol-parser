from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..params import CobolParserParams, CobolSourceFormat
from ..preprocessor.preprocessor import CobolPreprocessor


@dataclass
class CobolAnalysisResult:
    compilation_unit_name: str
    preprocessed_code: str
    parse_tree: object | None = None
    asg: object | None = None


class CobolParserRunner:
    def __init__(self) -> None:
        self._preprocessor = CobolPreprocessor()

    def analyze_code(
        self, cobol_code: str, compilation_unit_name: str, params: CobolParserParams
    ) -> CobolAnalysisResult:
        preprocessed_code = self._preprocessor.process_code(cobol_code, params)
        return CobolAnalysisResult(
            compilation_unit_name=compilation_unit_name,
            preprocessed_code=preprocessed_code,
            parse_tree=None,
            asg=None,
        )

    def analyze_file(self, cobol_file: Path, params: CobolParserParams) -> CobolAnalysisResult:
        preprocessed_code = self._preprocessor.process_file(cobol_file, params)
        return CobolAnalysisResult(
            compilation_unit_name=cobol_file.stem[:1].upper() + cobol_file.stem[1:],
            preprocessed_code=preprocessed_code,
            parse_tree=None,
            asg=None,
        )

    def analyze_file_with_format(
        self, cobol_file: Path, source_format: CobolSourceFormat
    ) -> CobolAnalysisResult:
        params = CobolParserParams(format=source_format, copybook_directories=[cobol_file.parent])
        return self.analyze_file(cobol_file, params)
