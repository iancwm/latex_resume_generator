# Specification

## Overview
This track implements several workflow and extensibility enhancements to the LaTeX Resume Generator:
1. A new CLI-based interactive menu tool (using `simple-term-menu`) to guide users through inputting their resume details, saving the output as draft YAML files to prevent data loss.
2. Introduction of `just` (via a `Justfile`) for robust build automation, replacing the existing shell script.
3. Migration to `uv` for faster and more reliable Python package management, while maintaining `requirements.txt` for backward compatibility.
4. Refactoring the template library into a configuration file (`config.yaml`) with detailed metadata for each template, improving extensibility.

## Functional Requirements
- **CLI Input Menu:**
  - Introduce an interactive CLI command (e.g., `generate-interactive`) using `simple-term-menu`.
  - Guide the user step-by-step to input fields for `public.yaml` and `private.yaml`.
  - Save the completed data into draft files (e.g., `draft_public.yaml`, `draft_private.yaml`).
- **Justfile Automation:**
  - Create a `Justfile` defining tasks: `build` (compiles PDFs), `clean` (removes LaTeX artifacts like .aux, .log, .out), `test` (runs pytest), `install` (uses `uv` to sync dependencies), and `archive` (moves old user information YAML files to a timestamped `archive/` folder).
- **uv Integration:**
  - Update documentation and setup instructions to use `uv` for creating the virtual environment and installing packages.
  - Implement a mechanism (e.g., a Just command) to generate/update `requirements.txt` from `uv`'s lockfile or `pyproject.toml` to maintain compatibility.
- **Template Configuration:**
  - Move the hardcoded `TEMPLATE_REGISTRY` from `src/main.py` into `config.yaml`.
  - The configuration structure must support detailed metadata (name, description, tags, file_path) for each template.
  - Update `src/main.py` and `src/engine.py` to read template availability and paths from `config.yaml`.

## Non-Functional Requirements
- **Dependencies:** Add `simple-term-menu` to the project's dependencies.
- **Backward Compatibility:** Existing `requirements.txt` based installation must continue to work. Existing `public.yaml` and `private.yaml` files must not be overwritten automatically by the new interactive CLI.
- **UX:** The interactive CLI should be intuitive and handle terminal resizing gracefully (handled by `simple-term-menu`).

## Acceptance Criteria
- [ ] Running the interactive CLI command prompts the user for all necessary resume fields and successfully generates draft YAML files.
- [ ] Running `just build` compiles the PDF using the configured template.
- [ ] Running `just clean` successfully removes all intermediate LaTeX build artifacts.
- [ ] Running `just archive` moves existing input YAMLs to an `archive/YYYYMMDD_HHMMSS/` directory.
- [ ] The project can be installed using `uv pip install -r requirements.txt` (or similar `uv` workflow).
- [ ] Adding a new template only requires editing `config.yaml` and placing the `.tex` file in the appropriate directory; no Python code changes are needed.
- [ ] All tests pass when run via `just test`.

## Out of Scope
- Modifying the LaTeX template visual designs.
- Implementing a full Web GUI (sticking to CLI).
- Complete removal of `pip`/`venv` support (must maintain compatibility).