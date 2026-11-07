# Saavan desktop integration

This fork is based on OpenJarvis commit c5a7766e04d4d7dc114d3182bd07914f45a48b2d.
The Apache-2.0 license and upstream notices remain in this repository.

`openjarvis.saavan.reviewer` adapts NativeReActAgent and OllamaEngine for the
existing Saavan desktop app. It receives a redacted source snapshot over stdin
and exposes only a read_selected_source tool. There are no file, shell, browser,
mail, or calendar tools. The desktop bridge enforces cancellation, timeout, source
hash checks, and scoped path validation before launching the child process.

Input JSON: source (numbered text), goal, host (local HTTP Ollama), model.
Output JSON: draft, question, turns, source_reads; errors exit nonzero.
Maximum four model turns. The application reads the source tool before generation, so even models that skip
tool calls receive the selected evidence. Exhausted or malformed agent results
are rejected. Findings remain model-generated and require review. No tests run.

Run from the fork with the existing Saavan Python environment and `PYTHONPATH=src`:
`python -m pytest -c /dev/null examples/saavan/test_reviewer.py`

This integration does not enable upstream proactive actions, automatic sending,
SDK tool discovery, remote models or Rust-backed memory. Existing Saavan voice,
project memory and task execution remain in the companion desktop repository.

## Shared desktop runtime

`openjarvis.saavan.runtime.DesktopRuntime` builds the shared OpenJarvis system
used by Saavan's local chat and structured background work. See
[UNIFIED_RUNTIME.md](UNIFIED_RUNTIME.md) for the capability matrix, native build,
setup and verification. Test with `test_runtime.py` alongside `test_reviewer.py`.
