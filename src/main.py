import os
import yaml
import typer
from simple_term_menu import TerminalMenu

from src.engine import generate as engine_generate
from src.config import load_config

app = typer.Typer()

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
            doc_type = "resume" if "resume" in file_path else "cover_letter"
            registry[doc_type][name] = {"path": file_path, "description": description}
    return registry

def get_default_template_name(doc_type: str) -> str:
    config = load_config()
    defaults = config.get("defaults", {})
    fallback_map = {"resume_template": "modern", "cover_letter_template": "standard"}
    config_key = f"{doc_type}_template"
    fallback = fallback_map.get(config_key)
    configured = defaults.get(config_key, fallback)
    registry = get_template_registry()
    if configured not in registry[doc_type]:
        return fallback
    return configured

def resolve_template_path(doc_type: str, template_name: str | None) -> tuple[str, str]:
    registry = get_template_registry()
    selected = template_name or get_default_template_name(doc_type)
    templates = registry[doc_type]
    if selected not in templates:
        valid = ", ".join(sorted(templates.keys()))
        raise typer.BadParameter(f"Unknown {doc_type} template '{selected}'. Valid options: {valid}")
    return selected, templates[selected]["path"]

@app.command()
def generate_resume(
    private: str = "inputs/private.yaml",
    public: str = "inputs/public.yaml",
    template_name: str | None = typer.Option(None, "--template-name", help="Resume template name."),
    output: str = "dist/resume.tex",
    redacted: bool = False,
    compile: bool = typer.Option(False, "--compile", help="Compile to PDF.")
):
    selected_template, template_path = resolve_template_path("resume", template_name)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    engine_generate(private, public, template_path, output, redacted, compile=compile)
    print("Resume generated successfully.")

@app.command()
def generate_cover_letter(
    private: str = "inputs/private.yaml",
    public: str = "inputs/public.yaml",
    template_name: str | None = typer.Option(None, "--template-name", help="Cover letter template name."),
    output: str = "dist/cover_letter.tex",
    redacted: bool = False,
    compile: bool = typer.Option(False, "--compile", help="Compile to PDF.")
):
    selected_template, template_path = resolve_template_path("cover_letter", template_name)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    engine_generate(private, public, template_path, output, redacted, compile=compile)
    print("Cover letter generated successfully.")

@app.command()
def list_templates():
    registry = get_template_registry()
    typer.echo(f"Resume templates (default: {get_default_template_name('resume')}):")
    for name, data in registry["resume"].items():
        typer.echo(f"  - {name}: {data['description']}")
    typer.echo(f"\nCover letter templates (default: {get_default_template_name('cover_letter')}):")
    for name, data in registry["cover_letter"].items():
        typer.echo(f"  - {name}: {data['description']}")

@app.command()
def generate_interactive():
    """
    Interactively input resume details and save as draft YAML files.
    """
    typer.echo("Welcome to the Interactive Resume Builder!")
    
    # Initialize empty data structures with default hierarchy
    private_data = {"basics": {"location": {}}}
    public_data = {"work": [], "education": [], "skills": [], "projects": []}

    # Load existing data if available
    if os.path.exists("inputs/private.yaml"):
        with open("inputs/private.yaml", "r") as f:
            existing_private = yaml.safe_load(f)
            if isinstance(existing_private, dict):
                for k, v in existing_private.items():
                    private_data[k] = v
                # Ensure hierarchy is maintained
                if not isinstance(private_data.get("basics"), dict):
                    private_data["basics"] = {}
                if not isinstance(private_data["basics"].get("location"), dict):
                    private_data["basics"]["location"] = {}
    
    if os.path.exists("inputs/public.yaml"):
        with open("inputs/public.yaml", "r") as f:
            existing_public = yaml.safe_load(f)
            if isinstance(existing_public, dict):
                for k, v in existing_public.items():
                    public_data[k] = v

    def edit_basics():
        while True:
            options = ["Name", "Email", "Phone", "Location (City)", "Location (Region)", "Back"]
            menu = TerminalMenu(options, title="Basics (Private Data)")
            choice = menu.show()
            if choice == 0: private_data["basics"]["name"] = input("Name: ")
            elif choice == 1: private_data["basics"]["email"] = input("Email: ")
            elif choice == 2: private_data["basics"]["phone"] = input("Phone: ")
            elif choice == 3: private_data["basics"]["location"]["city"] = input("City: ")
            elif choice == 4: private_data["basics"]["location"]["region"] = input("Region: ")
            elif choice == 5 or choice is None: break

    while True:
        main_options = ["Basics", "Work Experience (Public)", "Education (Public)", "Save and Exit", "Exit without Saving"]
        main_menu = TerminalMenu(main_options, title="Main Menu")
        main_choice = main_menu.show()

        if main_choice == 0:
            edit_basics()
        elif main_choice == 3:
            with open("draft_private.yaml", "w") as f:
                yaml.dump(private_data, f)
            with open("draft_public.yaml", "w") as f:
                yaml.dump(public_data, f)
            typer.echo("Saved interactive drafts to draft_private.yaml and draft_public.yaml")
            break
        elif main_choice == 4 or main_choice is None:
            break
        else:
            typer.echo("Feature coming soon!")

if __name__ == "__main__":
    app()
