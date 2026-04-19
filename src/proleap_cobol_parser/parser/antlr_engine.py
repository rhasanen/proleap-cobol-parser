from __future__ import annotations

import importlib
from dataclasses import dataclass

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener


class ParserNotGeneratedError(RuntimeError):
    pass


@dataclass
class CobolParseResult:
    parse_tree: object
    syntax_errors: int


class _ThrowingSyntaxErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e) -> None:  # type: ignore[override]
        raise SyntaxError(f"line {line}:{column} {msg}")


class _CountingSyntaxErrorListener(ErrorListener):
    def __init__(self) -> None:
        self.count = 0

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e) -> None:  # type: ignore[override]
        self.count += 1


class CobolAntlrParserEngine:
    def _load_generated_classes(self) -> tuple[type, type]:
        try:
            lexer_module = importlib.import_module(f"{__package__}.generated.CobolLexer")
            parser_module = importlib.import_module(f"{__package__}.generated.CobolParser")
        except ModuleNotFoundError as exc:
            raise ParserNotGeneratedError(
                "Generated ANTLR parser modules are missing. Run "
                "'python scripts/generate_python_antlr.py' "
                "from the repository root."
            ) from exc

        return lexer_module.CobolLexer, parser_module.CobolParser

    def is_available(self) -> bool:
        try:
            self._load_generated_classes()
            return True
        except ParserNotGeneratedError:
            return False

    def parse(self, preprocessed_code: str, ignore_syntax_errors: bool) -> CobolParseResult:
        cobol_lexer_cls, cobol_parser_cls = self._load_generated_classes()

        lexer = cobol_lexer_cls(InputStream(preprocessed_code))
        parser = cobol_parser_cls(CommonTokenStream(lexer))

        if ignore_syntax_errors:
            counting = _CountingSyntaxErrorListener()
            lexer.removeErrorListeners()
            parser.removeErrorListeners()
            lexer.addErrorListener(counting)
            parser.addErrorListener(counting)
            parse_tree = parser.startRule()
            return CobolParseResult(parse_tree=parse_tree, syntax_errors=counting.count)

        throwing = _ThrowingSyntaxErrorListener()
        lexer.removeErrorListeners()
        parser.removeErrorListeners()
        lexer.addErrorListener(throwing)
        parser.addErrorListener(throwing)
        parse_tree = parser.startRule()
        return CobolParseResult(parse_tree=parse_tree, syntax_errors=0)
