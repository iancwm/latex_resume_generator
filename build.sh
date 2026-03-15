#!/bin/bash
set -e

# Activate venv if it exists, otherwise assume global python
if [ -d "venv" ]; then
    PYTHON="./venv/bin/python3"
else
    PYTHON="python3"
fi

# Generate Resume TeX
echo "Generating Resume TeX..."
$PYTHON src/main.py generate-resume

# Generate Cover Letter TeX
echo "Generating Cover Letter TeX..."
$PYTHON src/main.py generate-cover-letter

# Build PDFs
echo "Building Resume PDF..."
xelatex -output-directory=dist dist/resume.tex
xelatex -output-directory=dist dist/resume.tex # Run twice for references

echo "Building Cover Letter PDF..."
xelatex -output-directory=dist dist/cover_letter.tex
xelatex -output-directory=dist dist/cover_letter.tex # Run twice for references

# Cleanup
echo "Cleaning up auxiliary files..."
rm -f dist/*.aux dist/*.log dist/*.out

echo "Build complete. Check dist/ folder."
