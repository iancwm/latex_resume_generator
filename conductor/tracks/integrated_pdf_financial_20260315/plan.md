# Implementation Plan - Integrated PDF Compilation and Financial Career Template

## Phase 1: Engine Integration ## Phase 1: Engine Integration & Automated PDF Generation Automated PDF Generation [checkpoint: 1d87a54]

1. **Integrated PDF Compilation**
   - [x] Task: Write tests for `compile_pdf` function [9a70a74] (mocking subprocess calls)
   - [x] Task: Implement `compile_pdf(tex_path, output_dir)` [67ffdd1] in `src/engine.py`
   - [x] Task: Update `generate` in `engine.py` to optionally compile PDF [c275c6c]
2. **CLI Update**
   - [x] Task: Add `--compile` flag [35c99c5] to `generate-resume` and `generate-cover-letter` commands in `src/main.py`
3. **Phase Checkpoint**
   - [x] Task: Conductor - User Manual Verification 'Engine Integration    - [ ] Task: Conductor - User Manual Verification 'Engine Integration & Automated PDF Generation' Automated PDF Generation' [1d87a54] (Protocol in workflow.md)

## Phase 2: Financial Template Development [checkpoint: 921c32b]

1. **Template Creation**
   - [x] Task: Create `templates/resume/financial.tex` [7236d5e] with finance-specific layout
   - [x] Task: Register the `financial` template [7236d5e] in `TEMPLATE_REGISTRY` in `src/main.py`
2. **Template Validation**
   - [x] Task: Verify the new template renders correctly [5073e67] with existing and new finance data
3. **Phase Checkpoint**
   - [x] Task: Conductor - User Manual Verification 'Financial Template Development' [921c32b] (Protocol in workflow.md)

## Phase 3: Enhanced Privacy Overrides

1. **Privacy Logic Enhancement**
   - [x] Task: Write tests for field-level privacy overrides [ccfb48b] (e.g., overriding global public/private settings)
   - [x] Task: Update `redact_data` in `src/engine.py` [ccfb48b] to support explicit override markers in YAML
2. **Verification**
   - [ ] Task: Confirm that overrides work as expected across nested YAML structures
3. **Phase Checkpoint**
   - [ ] Task: Conductor - User Manual Verification 'Enhanced Privacy Overrides' (Protocol in workflow.md)

## Phase 4: Final Integration & Cleanup

1. **Integration Test**
   - [ ] Task: Run full generation pipeline for a financial resume with redaction and PDF compilation
2. **Documentation**
   - [ ] Task: Update `README.md` to reflect the new `--compile` flag and `financial` template
3. **Phase Checkpoint**
   - [ ] Task: Conductor - User Manual Verification 'Final Integration & Cleanup' (Protocol in workflow.md)
