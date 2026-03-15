import os

import typer
import yaml

from engine import generate as engine_generate

app = typer.Typer()

TEMPLATE_REGISTRY = {
    "resume": {
        "modern": {
            "path": "resume/modern.tex",
            "description": "Modern resume design",
        },
        "classic": {
            "path": "resume/classic.tex",
            "description": "Traditional resume layout",
        },
        "minimal": {
            "path": "resume/minimal.tex",
            "description": "Minimal single-column resume",
        },
    },
    "cover_letter": {
        "standard": {
            "path": "cover_letter/standard.tex",
            "description": "Standard cover letter",
        },
        "formal": {
            "path": "cover_letter/formal.tex",
            "description": "Formal cover letter style",
        },
    },
}

FALLBACK_DEFAULTS = {
    "resume_template": "modern",
    "cover_letter_template": "standard",
}


def load_config(config_path: str = "config.yaml") -> dict:
    if not os.path.exists(config_path):
        return {}

    with open(config_path, "r") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        return {}

    return data


def get_default_template_name(doc_type: str) -> str:
    config = load_config()
    defaults = config.get("defaults", {})

    if not isinstance(defaults, dict):
        defaults = {}

    config_key = f"{doc_type}_template"
    fallback = FALLBACK_DEFAULTS[config_key]
    configured = defaults.get(config_key, fallback)

    if configured not in TEMPLATE_REGISTRY[doc_type]:
        return fallback

    return configured


def resolve_template_path(doc_type: str, template_name: str | None) -> tuple[str, str]:
    selected = template_name or get_default_template_name(doc_type)
    templates = TEMPLATE_REGISTRY[doc_type]

    if selected not in templates:
        valid = ", ".join(sorted(templates.keys()))
        raise typer.BadParameter(
            f"Unknown {doc_type} template '{selected}'. Valid options: {valid}"
        )

    template_path = os.path.join("templates", templates[selected]["path"])
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
    List available templates from the hardcoded registry.
    """
    resume_default = get_default_template_name("resume")
    cover_default = get_default_template_name("cover_letter")

    typer.echo(f"Resume templates (default: {resume_default}):")
    for name, data in TEMPLATE_REGISTRY["resume"].items():
        typer.echo(f"  - {name}: {data['description']}")

    typer.echo("")
    typer.echo(f"Cover letter templates (default: {cover_default}):")
    for name, data in TEMPLATE_REGISTRY["cover_letter"].items():
        typer.echo(f"  - {name}: {data['description']}")

if __name__ == "__main__":
    app()
