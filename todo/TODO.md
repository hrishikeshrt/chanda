# TODO

## Near-term (v1.0.x)
- [ ] Validate current CSV definitions in CI (fail on malformed rows).
- [ ] Document current definition format and contribution expectations.
- [ ] Add a CLI subcommand to validate definition files.
- [ ] Add a CLI subcommand to summarize meter stats from definitions.
- [ ] Normalize lakshana parsing into a shared helper with tests.

## Improvements
- [ ] Define a canonical definitions schema with explicit type (akshara/matra), pada_count, and pattern_kind.
- [ ] Add a 3-pada meter path in parsing/matching (explicit pada_count support).
- [ ] Remove heuristic pada inference in definitions; require explicit pada_index or pada_count.
- [ ] Make summarize_results a standalone helper module (avoid class coupling).
- [ ] Add round-trip tests for new schema conversion (CSV ↔ YAML/JSON).
- [ ] Track definition sources and versions per meter (metadata).
- [ ] Support per-meter constraints (final syllable flexibility, optional syllables).

## Potential Scripts
- [ ] `migrate_definitions.py`: convert existing CSV files to a canonical YAML/JSON schema.
- [ ] `validate_definitions.py`: check required fields, pada_count consistency, and pattern_kind.
- [ ] `build_signatures.py`: precompute LG signatures and multi-pada signatures.
- [ ] `lint_patterns.py`: detect invalid gana/LG tokens and trailing/leading whitespace.
- [ ] `generate_examples.py`: extract examples from examples.json for docs/tests.
- [ ] `diff_definitions.py`: compare two definition sources for regressions.
