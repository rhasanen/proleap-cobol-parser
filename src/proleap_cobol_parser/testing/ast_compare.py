from __future__ import annotations

from pathlib import Path
import re


def normalize_tree(tree: str) -> str:
    tree_no_escaped_newline = tree.replace("\\r", "").replace("\\n", "")
    tree_no_newline = tree_no_escaped_newline.replace("\r", "").replace("\n", "")
    tree_reduced_whitespace = re.sub(r"[\s]+", " ", tree_no_newline)
    tree_no_space_before_paren = re.sub(r"[\s]+\)", ")", tree_reduced_whitespace)
    return tree_no_space_before_paren.strip()


def compare_tree_with_file(actual_tree: str, expected_tree_file: Path, charset: str = "utf-8") -> bool:
    expected_tree = expected_tree_file.read_text(encoding=charset)
    return normalize_tree(actual_tree) == normalize_tree(expected_tree)

