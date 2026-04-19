#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import urllib.request


ANTLR_VERSION = "4.13.2"
ANTLR_JAR_NAME = f"antlr-{ANTLR_VERSION}-complete.jar"
ANTLR_DOWNLOAD_URL = f"https://www.antlr.org/download/{ANTLR_JAR_NAME}"

REPO_ROOT = Path(__file__).resolve().parents[1]
GRAMMAR_DIR = REPO_ROOT / "src/main/antlr4/io/proleap/cobol"
OUTPUT_DIR = REPO_ROOT / "src/proleap_cobol_parser/parser/generated"
CACHE_DIR = REPO_ROOT / ".cache" / "antlr"


def resolve_antlr_jar() -> Path:
    cache_jar = CACHE_DIR / ANTLR_JAR_NAME
    cache_jar.parent.mkdir(parents=True, exist_ok=True)

    if cache_jar.exists():
        return cache_jar

    urllib.request.urlretrieve(ANTLR_DOWNLOAD_URL, cache_jar)
    return cache_jar


def generate(grammar_name: str, antlr_jar: Path) -> None:
    grammar = GRAMMAR_DIR / grammar_name
    command = [
        "java",
        "-jar",
        str(antlr_jar),
        "-Dlanguage=Python3",
        "-visitor",
        "-no-listener",
        "-o",
        str(OUTPUT_DIR),
        str(grammar),
    ]
    subprocess.run(command, check=True)


def main() -> None:
    antlr_jar = resolve_antlr_jar()

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "__init__.py").write_text(
        '"""Generated ANTLR parser modules live in this package."""\n',
        encoding="utf-8",
    )

    generate("Cobol.g4", antlr_jar)
    generate("CobolPreprocessor.g4", antlr_jar)


if __name__ == "__main__":
    main()

