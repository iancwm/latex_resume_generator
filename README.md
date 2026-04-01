# YAML-to-LaTeX Resume & Cover Letter Generator

Generate beautiful, ATS-friendly LaTeX resumes and cover letters from structured YAML data.

## Features

- **Privacy-First**: Separate your private PII (name, contact info) from public professional data.
- **Enhanced Redaction Mode**: Generate redacted versions for sharing publicly. Includes field-level overrides to force specific fields to be public or private.
- **Integrated PDF Compilation**: Direct PDF generation using `xelatex` integrated into the Python engine.
- **Specialized Templates**: Includes Modern, Classic, Minimal, and Financial Career resume templates, plus Formal and Standard cover letter templates.
- **LaTeX Automation**: Automatic character escaping, smart quote handling, and protection against empty environments (e.g., empty itemize blocks).
- **Clean Output**: Build artifacts are automatically cleaned up, leaving only the final PDF.
- **TUI Editor**: Terminal-based interactive editor with live preview and session management.
- **Web Editor**: Browser-based form editor for resume data (works on Windows, WSL, Linux, macOS).
- **Preview Server**: Live preview server with PDF viewing and auto-refresh on compile.
- **Session Management**: Save and load editing sessions stored in `.sessions/` directory with atomic file writes (0600 permissions).
- **Interactive CLI Wizard**: Step-by-step input for resume data with validation (dates, email, bullet consistency).
- **Undo/Redo Support**: Full undo/redo functionality in the TUI editor with configurable state history.

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

7. **TUI Editor**:
   ```bash
   # Launch terminal-based editor
   python3 src/main.py edit

   # Edit cover letter
   python3 src/main.py edit --cover-letter

   # Use specific session
   python3 src/main.py edit --session my-session
   ```

8. **Web Editor**:
   ```bash
   # Launch browser-based editor
   python3 src/main.py web

   # Specify port and session
   python3 src/main.py web --port 8080 --session my-session

   # Don't auto-open browser
   python3 src/main.py web --no-open
   ```

9. **Preview Server**:
   ```bash
   # Start preview server (default port 8000)
   python3 src/main.py preview

   # Custom port
   python3 src/main.py preview --port 8080

   # Stop running server
   python3 src/main.py preview --stop
   ```

10. **Session Management**:
    ```bash
    # List all sessions
    python3 src/main.py sessions --list

    # Delete a session
    python3 src/main.py sessions --delete my-session
    ```

11. **Interactive CLI Wizard**:
    ```bash
    # Interactive input for resume data
    python3 src/main.py generate-interactive
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

Available templates:
- **Resume**: modern, classic, minimal, financial
- **Cover Letter**: standard, formal

You can override config defaults with `--template-name` per command.

## Development & Testing

The project includes a comprehensive test suite for the engine and CLI:
To run tests, build, and other automation tasks, use `just`. First, install `just` (e.g., `cargo install just`).
```bash
# Run all tests
just test

# Build all documents
just build

# Clean auxiliary files
just clean

# Lint Python code
just lint

# Format Python code
just format
```

## Architecture

- **`src/engine.py`**: Core YAML-to-LaTeX generation engine
- **`src/main.py`**: CLI entry point with Typer commands
- **`src/tui_app.py`**: Terminal UI editor using Textual
- **`src/web_app.py`**: Browser-based form editor using FastAPI
- **`src/preview_server.py`**: Live preview server with PDF viewing
- **`src/session_manager.py`**: Session persistence with atomic writes
- **`src/undo_manager.py`**: Undo/redo state management
- **`src/validators.py`**: Input validation (email, dates, bullet consistency)
- **`src/config.py`**: Configuration loading
- **`src/sanitizer.py`**: Data sanitization and privacy handling
