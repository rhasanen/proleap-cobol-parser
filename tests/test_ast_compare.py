from pathlib import Path

from proleap_cobol_parser.testing.ast_compare import compare_tree_with_file, normalize_tree


def test_normalize_tree_matches_java_cleanup_behavior() -> None:
    raw = "(startRule\\n  (compilationUnit \n\t(programUnit )) )\n"
    assert normalize_tree(raw) == "(startRule (compilationUnit (programUnit)))"


def test_compare_tree_with_file_ignores_whitespace_and_escaped_newlines(tmp_path: Path) -> None:
    expected = tmp_path / "sample.cbl.tree"
    expected.write_text("(startRule (x))", encoding="utf-8")
    actual = "(startRule\\n   (x ) )\n"
    assert compare_tree_with_file(actual, expected)

