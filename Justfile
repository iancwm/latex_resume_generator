# Justfile for LaTeX Resume Generator

# --- Variables ---
PYTHON := "uv run python3" # Use uv run to ensure python from venv is used
DIST_DIR := "dist"
SRC_DIR := "src"
TESTS_DIR := "tests"
INPUTS_DIR := "inputs"
ARCHIVE_ROOT_DIR := "archive"

# --- Recipes ---

# Default recipe: build all documents
default: build

# Create a virtual environment with uv
venv:
  @echo "Creating virtual environment with uv..."
  uv venv

# Build all resumes and cover letters to PDF
build:
  @echo "Generating Resume TeX..."
  {{PYTHON}} {{SRC_DIR}}/main.py generate-resume
  @echo "Generating Cover Letter TeX..."
  {{PYTHON}} {{SRC_DIR}}/main.py generate-cover-letter
  @echo "Building Resume PDF..."
  xelatex -output-directory={{DIST_DIR}} {{DIST_DIR}}/resume.tex
  xelatex -output-directory={{DIST_DIR}} {{DIST_DIR}}/resume.tex # Run twice for references
  @echo "Building Cover Letter PDF..."
  xelatex -output-directory={{DIST_DIR}} {{DIST_DIR}}/cover_letter.tex
  xelatex -output-directory={{DIST_DIR}} {{DIST_DIR}}/cover_letter.tex # Run twice for references
  @echo "Build complete. Check {{DIST_DIR}}/ folder."

# Clean up auxiliary LaTeX files
clean:
  @echo "Cleaning up auxiliary files..."
  rm -f {{DIST_DIR}}/*.aux {{DIST_DIR}}/*.log {{DIST_DIR}}/*.out
  @echo "Clean complete."

# Run all tests
test:
  @echo "Running tests..."
  PYTHONPATH={{SRC_DIR}} {{PYTHON}} -m unittest discover {{TESTS_DIR}}

# Install dependencies using uv
install:
  @echo "Installing dependencies with uv..."
  uv pip install -r requirements.txt

# Archive old user input YAML files
archive:
  @echo "Archiving old user input YAML files..."
  TIMESTAMP=$(shell date +"%Y%m%d_%H%M%S")
  ARCHIVE_PATH="{{ARCHIVE_ROOT_DIR}}/$$TIMESTAMP"
  mkdir -p "$$ARCHIVE_PATH"
  mv {{INPUTS_DIR}}/*.yaml "$$ARCHIVE_PATH"/
  @echo "Old YAML files moved to $$ARCHIVE_PATH/."

# Sync requirements.txt from uv environment
sync-reqs:
  @echo "Generating requirements.txt from uv environment..."
  uv pip freeze > requirements.txt
  @echo "requirements.txt updated."

# Lint Python code
lint:
  @echo "Linting Python code with ruff..."
  uv run ruff check {{SRC_DIR}}

# Format Python code
format:
  @echo "Formatting Python code with ruff..."
  uv run ruff format {{SRC_DIR}}

PHONY: default build clean test install archive sync-reqs lint format venv