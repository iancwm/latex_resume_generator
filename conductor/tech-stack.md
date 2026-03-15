# Technology Stack - LaTeX Resume Generator

## Language & Core Runtime
- **Python 3.12+**: The primary programming language for the generator engine and CLI.
- **Virtual Environment (venv)**: Standardized Python environment isolation.

## CLI & Templating
- **Typer**: A modern, FastAPI-inspired library for building the command-line interface.
- **Jinja2**: The templating engine used to inject YAML data into LaTeX source files, configured with custom delimiters to avoid conflicts with LaTeX syntax.

## Data Processing
- **PyYAML**: For parsing and processing the structured input data (`private.yaml`, `public.yaml`).

## Document Generation
- **LaTeX (XeLaTeX)**: The backend for typesetting high-quality, professional documents.
- **Custom Sanitizer**: A bespoke module for escaping LaTeX special characters and handling smart quotes.

## Infrastructure & Build
- **Shell Scripting (build.sh)**: For orchestrating the generation and PDF compilation process.
- **Git**: Version control for tracking templates and code.
