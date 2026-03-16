import os

import typer
# import yaml # No longer needed, as config.py handles it

from src.engine import generate as engine_generate
from src.config import load_config # Import the centralized load_config

app = typer.Typer()

# Removed TEMPLATE_REGISTRY and FALLBACK_DEFAULTS

def get_template_registry() -> dict:
    """Loads and returns the template registry from config.yaml."""
    config = load_config()
    templates = config.get("templates", [])
    registry = {"resume": {}, "cover_letter": {}}
    for template in templates:
        name = template.get("name")
        file_path = template.get("file_path")
        description = template.get("description", "No description provided.")
        if name and file_path:
            doc_type = "resume" if "resume" in file_path else "cover_letter" # Simple heuristic
            registry[doc_type][name] = {"path": file_path, "description": description}
    return registry


def get_default_template_name(doc_type: str) -> str:
    config = load_config()
    defaults = config.get("defaults", {})

    if not isinstance(defaults, dict):
        defaults = {}

    config_key = f"{doc_type}_template"
    # FALLBACK_DEFAULTS is removed, define defaults here or in config.yaml
    fallback_map = {
        "resume_template": "modern",
        "cover_letter_template": "standard",
    }
    fallback = fallback_map.get(config_key)
    configured = defaults.get(config_key, fallback)

    # Validate against the loaded registry
    registry = get_template_registry()
    if configured not in registry[doc_type]:
        return fallback # Fallback to a known good default if configured is invalid

    return configured


def resolve_template_path(doc_type: str, template_name: str | None) -> tuple[str, str]:
    registry = get_template_registry()
    selected = template_name or get_default_template_name(doc_type)
    templates = registry[doc_type]

    if selected not in templates:
        valid = ", ".join(sorted(templates.keys()))
        raise typer.BadParameter(
            f"Unknown {doc_type} template '{selected}'. Valid options: {valid}"
        )

    # The template_path from config.yaml is already relative to the project root (e.g., templates/resume/modern.tex)
    template_path = templates[selected]["path"]
    return selected, template_path

@app.command()
def generate_resume(
    private: str = "inputs/private.yaml",
    public: str = "inputs/public.yaml",
    template_name: str | None = typer.Option(
        None,
        "--template-name",
        help="Resume template name from registry.",
    ),
    output: str = "dist/resume.tex",
    redacted: bool = False,
    compile: bool = typer.Option(
        False,
        "--compile",
        help="Compile the generated .tex file to PDF.",
    )
):
    """
    Generate a resume from YAML inputs.
    """
    selected_template, template_path = resolve_template_path("resume", template_name)
    print(
        f"Generating resume to {output} "
        f"(Template: {selected_template}, Redacted: {redacted}, Compile: {compile})..."
    )
    # Ensure dist directory exists
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    engine_generate(private, public, template_path, output, redacted, compile=compile)
    print("Resume generated successfully.")

@app.command()
def generate_cover_letter(
    private: str = "inputs/private.yaml",
    public: str = "inputs/public.yaml",
    template_name: str | None = typer.Option(
        None,
        "--template-name",
        help="Cover letter template name from registry.",
    ),
    output: str = "dist/cover_letter.tex",
    redacted: bool = False,
    compile: bool = typer.Option(
        False,
        "--compile",
        help="Compile the generated .tex file to PDF.",
    )
):
    """
    Generate a cover letter from YAML inputs.
    """
    selected_template, template_path = resolve_template_path(
        "cover_letter", template_name
    )
    print(
        f"Generating cover letter to {output} "
        f"(Template: {selected_template}, Redacted: {redacted}, Compile: {compile})..."
    )
    # Ensure dist directory exists
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    engine_generate(private, public, template_path, output, redacted, compile=compile)
    print("Cover letter generated successfully.")


@app.command()
def list_templates():
    """
    List available templates.
    """
    registry = get_template_registry()
    resume_default = get_default_template_name("resume")
    cover_default = get_default_template_name("cover_letter")

    typer.echo(f"Resume templates (default: {resume_default}):")
    for name, data in registry["resume"].items():
        typer.echo(f"  - {name}: {data['description']}")

    typer.echo("")
    typer.echo(f"Cover letter templates (default: {cover_default}):")
    for name, data in registry["cover_letter"].items():
        typer.echo(f"  - {name}: {data['description']}")

if __name__ == "__main__":
    app()
