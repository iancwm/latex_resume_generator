# Implementation Plan

## Phase 1: Tooling and Infrastructure (uv & just) [checkpoint: 33c1a15]
- [x] Task: Update project documentation and setup instructions to use `uv` for dependency management.
- [x] Task: Create `Justfile` and implement `build`, `clean`, `test`, `install`, and `archive` commands.
- [x] Task: Implement a command in `Justfile` to generate/update `requirements.txt` from `uv`.
- [~] Task: Conductor - User Manual Verification 'Phase 1: Tooling and Infrastructure (uv & just)' (Protocol in workflow.md)

## Phase 2: Configuration Driven Templates [checkpoint: fc96f72]
- [x] Task: Write failing tests for loading template registry from `config.yaml`.
- [x] Task: Update `config.yaml` with the detailed template metadata structure.
- [x] Task: Implement reading template configurations from `config.yaml` in `src/main.py` and `src/engine.py` to make tests pass.
- [x] Task: Refactor existing code to fully remove the hardcoded `TEMPLATE_REGISTRY`.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Configuration Driven Templates' [fc96f72] (Protocol in workflow.md)

## Phase 3: Interactive CLI Tool
- [x] Task: Add `simple-term-menu` to dependencies and update `requirements.txt`. [94d2d1b]
- [x] Task: Write failing tests for the `generate-interactive` Typer command and data saving logic (mocking prompts). [80b0461]
- [x] Task: Implement the Typer command `generate-interactive` in `src/main.py`. [b2fca38]
- [x] Task: Implement the interactive input workflow using `simple-term-menu`. [b2fca38]
- [x] Task: Implement logic to save the inputs to `draft_public.yaml` and `draft_private.yaml`. [b2fca38]
- [~] Task: Conductor - User Manual Verification 'Phase 3: Interactive CLI Tool' (Protocol in workflow.md)