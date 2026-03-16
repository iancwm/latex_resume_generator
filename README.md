# YAML-to-LaTeX Resume & Cover Letter Generator

Generate beautiful, ATS-friendly LaTeX resumes and cover letters from structured YAML data.

## Features

- **Privacy-First**: Separate your private PII (name, contact info) from public professional data.
- **Enhanced Redaction Mode**: Generate redacted versions for sharing publicly. Includes field-level overrides to force specific fields to be public or private.
- **Integrated PDF Compilation**: Direct PDF generation using `xelatex` integrated into the Python engine.
- **Specialized Templates**: Includes Modern, Classic, Minimal, and a dedicated **Financial Career** template.
- **LaTeX Automation**: Automatic character escaping, smart quote handling, and protection against empty environments (e.g., empty itemize blocks).
- **Clean Output**: Build artifacts are automatically cleaned up, leaving only the final PDF.

## Usage

1. **Install Dependencies**:
   First, install `uv` (e.g., `curl -LsSf https://astral.sh/uv/install.sh | sh`).
   Then, use `uv` to install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

2. **Configure Data**:
   Edit `inputs/private.yaml` and `inputs/public.yaml`. See [Field Metadata & Overrides](#field-metadata--overrides) below.

3. **Generate Resume**:
   ```bash
   # Generate .tex only
   python3 src/main.py generate-resume
   
   # Generate .tex and compile to .pdf
   python3 src/main.py generate-resume --compile
   ```

4. **List Available Templates**:
   ```bash
   python3 src/main.py list-templates
   ```

5. **Use a Specific Template**:
   ```bash
   python3 src/main.py generate-resume --template-name financial --compile
   python3 src/main.py generate-cover-letter --template-name formal --compile
   ```

6. **Redacted Version**:
   ```bash
   python3 src/main.py generate-resume --redacted --compile
   ```

## Field Metadata & Overrides

You can override the default privacy setting for any field by using a structured object instead of a string:

```yaml
email:
  value: "public.email@example.com"
  private: false # Force this field to be visible even in --redacted mode
```

Conversely, you can hide specific details in your public file:

```yaml
- company: "Top Secret Corp"
  position:
    value: "Lead Engineer"
    private: true # This will be redacted even in a normal run
```

## Template Configuration

Default templates are configured in root-level `config.yaml`:

```yaml
defaults:
  resume_template: modern
  cover_letter_template: standard
```

You can override config defaults with `--template-name` per command.

## Development & Testing

The project includes a comprehensive test suite for the engine and CLI:
To run tests, build, and other automation tasks, use `just`. First, install `just` (e.g., `cargo install just`).
```bash
# Run all tests
just test
```
