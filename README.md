# YAML-to-LaTeX Resume & Cover Letter Generator

Generate beautiful, ATS-friendly LaTeX resumes and cover letters from structured YAML data.

## Features

- **Privacy-First**: Separate your private PII (name, contact info) from public professional data.
- **Redaction Mode**: Generate redacted versions for sharing publicly or anonymously.
- **LaTeX Automation**: Automatic character escaping and smart quote handling.
- **Clean Output**: Build artifacts are automatically cleaned up, leaving only the final PDF.

## Usage

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Data**:
   Edit `inputs/private.yaml` and `inputs/public.yaml` according to the schema below.

3. **Generate Resume**:
   ```bash
   ./build.sh
   ```
   or manually:
   ```bash
   python3 src/main.py generate-resume
   ```

4. **List Available Templates**:
   ```bash
   python3 src/main.py list-templates
   ```

5. **Use a Specific Template**:
   ```bash
   python3 src/main.py generate-resume --template-name classic
   python3 src/main.py generate-cover-letter --template-name formal
   ```

6. **Redacted Version**:
   ```bash
   python3 src/main.py generate-resume --redacted
   ```

## Template Configuration

Default templates are configured in root-level `config.yaml`:

```yaml
defaults:
  resume_template: modern
  cover_letter_template: standard
```

You can override config defaults with `--template-name` per command.

## YAML Schema

### `inputs/private.yaml` (PII)
```yaml
basics:
  name: "Jane Doe"
  label: "Software Engineer"
  email: "jane.doe@example.com"
  phone: "(555) 123-4567"
  url: "https://janedoe.com"
  location:
    city: "San Francisco"
    region: "CA"
```

### `inputs/public.yaml` (Professional Data)
```yaml
work:
  - company: "Tech Corp"
    position: "Senior Developer"
    startDate: "2020-01"
    endDate: "Present"
    summary:
      - "Led a team of 5 engineers to build a scalable microservice architecture."
      - "Reduced latency by 40% through optimization."

education:
  - institution: "University of Technology"
    area: "B.S. Computer Science"
    startDate: "2016-09"
    endDate: "2020-05"

skills:
  - category: "Languages"
    keywords: ["Python", "JavaScript", "Rust"]
  - category: "Frameworks"
    keywords: ["Django", "React", "Typer"]

projects:
  - name: "Resume Generator"
    description: "A CLI tool to generate LaTeX resumes from YAML."
    url: "https://github.com/janedoe/resume-generator"
```
