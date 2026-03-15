# Specification: Integrated PDF Compilation and Financial Career Template

## Problem
Currently, PDF compilation is handled by a separate shell script (`build.sh`), which is not portable and lacks robust error handling. Additionally, there's no specialized template for financial careers, which often require specific layouts (e.g., more dense, different section headers). Privacy logic also needs more flexibility.

## Goal
- Integrate `xelatex` compilation directly into the Python `engine.py`.
- Create a new `financial` resume template.
- Enhance privacy logic to allow field-level overrides.

## Requirements
1. **Engine Integration**:
    - `compile_pdf` function in `engine.py`.
    - Error handling for missing `xelatex`.
2. **Templates**:
    - `templates/resume/financial.tex` based on standard financial career layouts.
    - Support for specialized headers (e.g., "Certifications", "Technical Skills").
3. **Privacy Overrides**:
    - Ability to mark a field as `private: true` or `private: false` in YAML to override defaults.
