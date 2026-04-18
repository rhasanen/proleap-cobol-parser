# Python Port Plan: proleap-cobol-parser

## 1) Current repository assessment

### Core architecture
- **ANTLR grammars**:  
  - `src/main/antlr4/io/proleap/cobol/Cobol.g4`
  - `src/main/antlr4/io/proleap/cobol/CobolPreprocessor.g4`
- **Preprocessing pipeline** (`io.proleap.cobol.preprocessor`):
  - Line reading and normalization for source formats (`FIXED`, `TANDEM`, `VARIABLE`)
  - Comment-entry handling
  - COPY / REPLACE / compiler options parsing
  - EXEC SQL / EXEC SQLIMS / EXEC CICS extraction tags
- **Parsing + semantic analysis pipeline** (`io.proleap.cobol.asg.runner.impl.CobolParserRunnerImpl`):
  - Preprocess input
  - Lex + parse with ANTLR
  - Multi-pass ASG build:
    1. program units
    2. data division step 1
    3. data division step 2
    4. file control clauses
    5. file description entry clauses
    6. procedure divisions
    7. procedure statements
- **ASG model** (`io.proleap.cobol.asg.metamodel`):
  - Large typed interface/implementation surface (~1000+ Java source files in `src/main/java`)
  - Registry-based semantic links (`ASGElementRegistry`)
- **Config surface** (`CobolParserParams`):
  - source format, dialect, charset, copybook directories/extensions/files, syntax-error behavior

### Test landscape
- Existing build: Maven + JUnit 4
- CI: `.github/workflows/test.yml` runs `mvn -T 1C test`
- Baseline run succeeded in this environment (`mvn -T 1C test`, exit code 0)
- Broad test corpus:
  - large Java test suite (`src/test/java`, including `gov/nist`)
  - NIST COBOL resources (`src/test/resources/gov/nist`)
  - AST fixtures (`.tree`) and preprocessor expected outputs (`.preprocessed`)

## 2) Target Python product definition

### Desired Python package
- Package name: `proleap_cobol_parser` (distribution can be `python-proleap-cobol-parser`)
- Public API parity with Java entrypoints:
  - parse/analyze from file or string
  - configurable source format and copybook resolution
  - access to parse tree and semantic model
- First-class compatibility goals:
  - preserve preprocessor behavior
  - preserve grammar coverage and parse tree expectations
  - preserve ASG semantics for commonly used constructs

### Recommended stack
- Python 3.11+ (or project policy minimum)
- ANTLR4 Python runtime (version aligned with grammar generation strategy)
- `pytest` for test migration
- `pydantic` not required; prefer stdlib `dataclasses` + typing unless strong validation needs emerge

## 3) Porting strategy (phased, low-risk)

## Phase 0 — Foundation and scope lock
- Define explicit compatibility contract:
  - which Java APIs are “must-keep”
  - which internals can be redesigned
- Freeze behavior baseline from current Java outputs:
  - parse trees for selected fixture matrix
  - preprocessor outputs for selected fixture matrix
  - ASG snapshots for selected semantic-heavy samples
- Produce a traceability matrix:
  - Java package/class -> Python module/class/function mapping

## Phase 1 — Python project scaffolding
- Initialize Python package structure:
  - `src/proleap_cobol_parser/...`
  - test layout mirroring Java test domain grouping
- Add packaging/tooling:
  - `pyproject.toml`
  - lint/type/test toolchain configuration
- Add deterministic grammar generation path:
  - command/script to generate parser from `Cobol.g4` + `CobolPreprocessor.g4`
  - commit policy for generated artifacts (committed vs generated-at-build) decided early

## Phase 2 — Port preprocessor first
- Recreate `CobolParserParams` equivalent in Python.
- Port source-format line handling:
  - fixed/tandem/variable line segmentation rules
  - indicator-column semantics
  - multiline comment-entry behavior
- Port document-level transforms:
  - COPY resolution
  - REPLACE handling (including edge cases from fixtures)
  - compiler options parsing coverage
  - EXEC SQL/SQLIMS/CICS extraction markers
- Validate against `.preprocessed` fixtures before parser integration.

## Phase 3 — ANTLR parser integration
- Generate Python lexer/parser from existing grammars.
- Implement parse runner equivalent to `CobolParserRunner`:
  - parse from string/file
  - error listener behavior parity
  - preprocessor -> lexer/parser data flow
- Implement AST comparison utilities for fixture-based parity checks.

## Phase 4 — Semantic model (ASG) migration in slices
- Do **not** port all 1:1 classes at once.
- Migrate by semantic layers aligned to existing visitor passes:
  1. core program/compilation unit graph + registry
  2. identification/environment/data minimal structure
  3. data-division clauses and symbol resolution
  4. file control + file description clauses
  5. procedure division shell
  6. statement families by priority (MOVE/IF/PERFORM/CALL/... then long tail)
- For each slice:
  - implement Python model classes
  - port corresponding visitors/analysis logic
  - lock parity with targeted fixture tests

## Phase 5 — Test migration and parity gates
- Build Python test harness equivalents of:
  - `CobolParseTestRunnerImpl` behavior for AST fixture checks
  - ASG assertion style used in Java tests
- Migrate tests in waves:
  - preprocessor tests first
  - AST tests second
  - ASG tests third
  - NIST suite last (optionally tagged/partitioned for runtime)
- Add parity CI matrix:
  - fast smoke subset on each push
  - full suite scheduled/nightly if runtime is high

## Phase 6 — Performance and packaging hardening
- Benchmark parse+analyze throughput on representative corpora.
- Optimize hotspots:
  - token walking
  - symbol resolution
  - repeated tree traversals
- Publish package artifacts and versioning policy.
- Provide migration guide for Java users to Python API equivalents.

## 4) Proposed Python module blueprint

- `proleap_cobol_parser/preprocessor/`
  - `formats.py` (format enums/rules)
  - `line_reader.py`, `line_rewriter.py`, `line_writer.py`
  - `copybook_resolver.py`, `document_parser.py`
- `proleap_cobol_parser/parser/`
  - ANTLR generated modules
  - `runner.py`, `errors.py`
- `proleap_cobol_parser/asg/`
  - `metamodel/` (dataclasses/protocols)
  - `registry.py`
  - `resolver.py`
  - `visitors/` (mirroring Java visitor stages)
- `proleap_cobol_parser/testing/`
  - fixture loaders
  - tree normalizers/comparators

## 5) Risk register and mitigations

- **Risk: semantic drift during ASG migration**
  - Mitigation: slice-by-slice parity gates and fixture baselines.
- **Risk: ANTLR runtime/version mismatch**
  - Mitigation: lock grammar generation/runtime versions and validate generated parser behavior early.
- **Risk: COPY/REPLACE corner cases regress**
  - Mitigation: preprocessor-first strategy and fixture-driven porting.
- **Risk: scale of metamodel (very large surface)**
  - Mitigation: prioritize high-usage statement families first; stage long tail.
- **Risk: NIST test runtime in Python CI**
  - Mitigation: split smoke/full pipelines and cache generated parser artifacts.

## 6) Definition of done

- Python package exposes stable parse/analyze APIs with documented parameters.
- Preprocessor fixture parity achieved for existing `.preprocessed` corpus.
- AST fixture parity achieved for existing `.tree` corpus.
- ASG parity achieved for prioritized statement families and core divisions.
- NIST suite reaches agreed pass-rate target (ideally parity with current Java behavior).
- CI green for lint/type/test and release pipeline produces installable package.
