# LaTeX Resume Generator - Agent Knowledge Base

## Overview

This is a YAML-to-LaTeX resume and cover letter generator. It generates ATS-friendly LaTeX documents from structured YAML data with privacy-first features (separate PII from professional data, redaction mode).

## Project Structure

```
latex_resume_generator/
├── config.yaml          # Default template selection
├── src/
│   ├── __init__.py
│   ├── main.py          # CLI entry point, template registry, config loading
│   ├── engine.py        # Core generation logic
│   └── sanitizer.py     # LaTeX escaping utilities
├── templates/
│   ├── resume/
│   │   ├── modern.tex
│   │   ├── classic.tex
│   │   └── minimal.tex
│   └── cover_letter/
│       ├── standard.tex
│       └── formal.tex
├── inputs/
│   ├── private.yaml     # PII (name, contact, location)
│   └── public.yaml      # Professional data (work, education, skills, projects)
├── dist/                # Generated output
├── build.sh             # Full build pipeline
└── requirements.txt
```

## Core Components

### CLI Commands (`src/main.py`)

- `generate-resume` - Generates resume from YAML inputs
- `generate-cover-letter` - Generates cover letter from YAML inputs
- `list-templates` - Lists template names and descriptions

Options:
- `--private` - Path to private YAML (default: `inputs/private.yaml`)
- `--public` - Path to public YAML (default: `inputs/public.yaml`)
- `--template-name` - Template key from hardcoded registry
- `--output` - Output path
- `--redacted` - Generate redacted version (replaces PII with `[KEY REDACTED]`)

Template selection behavior:
- Registry is hardcoded in `src/main.py`
- Defaults come from root `config.yaml`
- If config is missing or invalid, fallback defaults are used

### Engine (`src/engine.py`)

Functions:
- `load_yaml(path)` - Loads YAML file, returns empty dict if not found
- `redact_data(data)` - Recursively replaces string values with `[KEY REDACTED]`
- `sanitize_data(data)` - Applies LaTeX escaping and smart quotes recursively
- `render_template(template_path, output_path, context)` - Renders Jinja2 template
- `generate(...)` - Main pipeline: load → redact (optional) → sanitize → render

### Sanitizer (`src/sanitizer.py`)

- `escape_latex(text)` - Escapes LaTeX special characters: `& % $ # _ { } ~ ^ \`
- `smart_quotes(text)` - Converts `"text"` to `` ``text'' `` (LaTeX curly quotes)
- `sanitize(value)` - Applies both to strings, lists, or dicts

### Templates

Templates use custom Jinja2 delimiters for LaTeX compatibility:
- `\VAR{var}` - Variable interpolation
- `\BLOCK{for ...}` - Loops
- `%%` - Line statements

Available template variables from YAML:
- `basics` - name, label, email, phone, url, location (city, region)
- `work` - array of {company, position, startDate, endDate, summary[]}
- `education` - array of {institution, area, startDate, endDate}
- `skills` - array of {category, keywords[]}
- `projects` - array of {name, description, url}

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Generate resume
python3 src/main.py generate-resume

# Generate with specific templates
python3 src/main.py generate-resume --template-name classic
python3 src/main.py generate-cover-letter --template-name formal

# List available templates
python3 src/main.py list-templates

# Generate redacted version
python3 src/main.py generate-resume --redacted

# Full build (generates PDFs)
./build.sh
```

## Build Pipeline (`build.sh`)

1. Generate resume TeX via Python
2. Generate cover letter TeX via Python
3. Compile resume PDF (XeLaTeX, twice for refs)
4. Compile cover letter PDF (XeLaTeX, twice for refs)
5. Clean up auxiliary files (*.aux, *.log, *.out)

## Dependencies

- jinja2 - Template engine
- PyYAML - YAML parsing
- typer - CLI framework

## Design Patterns

- **Privacy separation**: Private YAML contains PII, public YAML contains professional data
- **Redaction**: Pass `--redacted` flag to replace private data with placeholders
- **Sanitization**: All string data automatically escaped for LaTeX before rendering
- **Template registry**: Template names are constrained by hardcoded registry keys
- **Config-driven defaults**: Root-level `config.yaml` defines default resume/cover-letter templates
- **Clean output**: Build artifacts cleaned, only final PDFs remain in dist/
