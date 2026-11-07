# Unified Saavan runtime

Saavan now initializes the OpenJarvis SystemBuilder once at backend startup.
Its local LLM requests (chat, preparation plans and structured source edits) go
through the shared engine, scanners, audit and local inference telemetry.
Cloud mode remains the existing explicitly configured alternative. The desktop
continues using Kokoro voice and its existing conversation/mission stores.

## Available in the desktop

- **Saavan runtime** shows live initialization status, model and configured tools.
- **Ask with tools and knowledge** uses the native ReAct agent, calculator and
  retrieval. It receives saved focus, unfinished tasks and current-project recent
  conversations. Results show which tools actually ran. Maximum four model turns.
- **Agent with tools and knowledge** runs through the persistent mission queue.
- `use tools to ...` in the regular command field invokes the same agent path.
- **Searchable project knowledge** indexes a selected source/text file locally,
  replaces its old indexed copy when re-added, searches with native FTS, and removes
  indexed copies without touching source files. The existing 60 KB and path limits
  apply. Indexed files are shared across projects; conversation recall stays scoped.
- Source reviews continue using the bounded OpenJarvis review adapter.

## Ready components versus active services

The native extension, inference, guarded tool execution, native knowledge store,
local telemetry and audit are active. The OpenJarvis session store, workflow
engine, scheduler store, agent manager and skill manager are initialized and
available as integration primitives. They are not a second background execution
service. Saavan's mission queue, reviewed linked plans and project conversation
store remain authoritative. No scheduled task is created by installing this.

External messaging/calendar/email channels, cloud accounts, remote MCP servers,
browser automation, container sandboxes, additional GPU engines and autonomous
training are not configured. They require their own accounts, credentials,
runtimes or explicit task scopes. Installing a framework does not make all those
services usable. The runtime panel reports this rather than claiming everything
is active. Arbitrary shell/file tools are not exposed to the conversational agent;
existing explicitly scoped edit/build/test tasks still handle local changes.

## Local state and retention

State is under backend/storage/framework (ignored by Git). Knowledge persists
until its indexed copy is removed. It is separate from conversation-memory
clearing and its 30-day retention. Existing heuristic redaction applies to indexed
files; it does not guarantee removal of every private detail. External usage
analytics are disabled. Local telemetry and audit remain enabled.

The async adapter bounds pending requests to six and serializes model operations.
Cancellation of a caller does not incorrectly free capacity while its read-only
worker is still running. Existing source-edit cancellation guards still apply.

## Setup and launch

The sibling OpenJarvis checkout must be on codex/saavan-desktop-integration.
The current Mac has the native extension compiled and installed in backend/venv.
It was built from the fork's Rust source; no external prebuilt binary was used.

From backend with its virtual environment active:

    python scripts/setup_framework.py --check

For a new environment, install backend requirements, Rust >=1.88 and the platform
compiler, then run:

    python scripts/setup_framework.py --build-native

Or install a matching locally built wheel with `--native-wheel PATH`.
The fork is installed editable without replacing the desktop environment with
all optional upstream extras. Start the app using `bash run_saavan.sh`.
If framework startup fails, status exposes the failure; it is not reported ready.

## Verification

Integration tests: examples/saavan/test_runtime.py in the fork and
backend/tests/test_framework_service.py in the desktop app. Native tests cover
component initialization, indexed-copy replacement/removal, structured output,
final-answer cleanup and agent failure. Desktop tests cover serialization across
caller cancellation and shutdown. Existing voice, plans, memory, checks and review
regressions remain in the companion test suite.

## Live verification and limits

The runtime panel successfully performed a calculator-backed answer and indexed
and retrieved a temporary document through the native store. The test index was
removed afterward. Native component initialization and the existing desktop test
suite pass. Structured tasks retain Saavan's Ollama `/api/generate` prompt framing
inside the guarded OpenJarvis engine; ordinary chat uses its chat API.

A separate behavior test exposed a local-model code-generation mistake: an edit
passed a narrow existing test but failed the requested string-input behavior.
Framework integration does not make generated edits automatically correct. Use
behavior-specific acceptance tests before relying on them. The task result only
claims the selected check passed; it does not certify all requested behavior.
