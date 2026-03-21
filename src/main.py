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

    def input_list(prompt_msg):
        items = []
        typer.echo(f"{prompt_msg} (Enter empty line to finish)")
        while True:
            item = input("> ")
            if not item:
                break
            items.append(item)
        return items

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

    def edit_work():
        while True:
            options = ["Add Entry", "Edit Entry", "Remove Entry", "Back"]
            menu = TerminalMenu(options, title="Work Experience (Public Data)")
            choice = menu.show()
            if choice == 0:
                entry = {"company": "", "position": "", "location": "", "startDate": "", "endDate": "", "summary": []}
                while True:
                    e_options = ["Company", "Position", "Location", "Start Date", "End Date", "Summary", "Back"]
                    e_menu = TerminalMenu(e_options, title=f"Add Work Entry: {entry['company'] or 'New'}")
                    e_choice = e_menu.show()
                    if e_choice == 0: entry["company"] = input("Company: ")
                    elif e_choice == 1: entry["position"] = input("Position: ")
                    elif e_choice == 2: entry["location"] = input("Location: ")
                    elif e_choice == 3: entry["startDate"] = input("Start Date (YYYY-MM): ")
                    elif e_choice == 4: entry["endDate"] = input("End Date (YYYY-MM/Present): ")
                    elif e_choice == 5: entry["summary"] = input_list("Summary Points")
                    elif e_choice == 6 or e_choice is None: break
                public_data["work"].append(entry)
            elif choice == 3 or choice is None: break
            else: typer.echo("Edit/Remove coming soon!")

    def edit_education():
        while True:
            options = ["Add Entry", "Edit Entry", "Remove Entry", "Back"]
            menu = TerminalMenu(options, title="Education (Public Data)")
            choice = menu.show()
            if choice == 0:
                entry = {"institution": "", "area": "", "location": "", "startDate": "", "endDate": "", "score": "", "honors": [], "courses": []}
                while True:
                    e_options = ["Institution", "Area", "Location", "Start Date", "End Date", "Score/GPA", "Honors", "Courses", "Back"]
                    e_menu = TerminalMenu(e_options, title=f"Add Education Entry: {entry['institution'] or 'New'}")
                    e_choice = e_menu.show()
                    if e_choice == 0: entry["institution"] = input("Institution: ")
                    elif e_choice == 1: entry["area"] = input("Area of Study: ")
                    elif e_choice == 2: entry["location"] = input("Location: ")
                    elif e_choice == 3: entry["startDate"] = input("Start Date (YYYY-MM): ")
                    elif e_choice == 4: entry["endDate"] = input("End Date (YYYY-MM): ")
                    elif e_choice == 5: entry["score"] = input("Score/GPA: ")
                    elif e_choice == 6: entry["honors"] = input_list("Honors")
                    elif e_choice == 7: entry["courses"] = input_list("Courses")
                    elif e_choice == 8 or e_choice is None: break
                public_data["education"].append(entry)
            elif choice == 3 or choice is None: break
            else: typer.echo("Edit/Remove coming soon!")

    def edit_skills():
        while True:
            options = ["Add Category", "Edit Category", "Remove Category", "Back"]
            menu = TerminalMenu(options, title="Skills (Public Data)")
            choice = menu.show()
            if choice == 0:
                entry = {"category": "", "keywords": []}
                while True:
                    e_options = ["Category Name", "Keywords", "Back"]
                    e_menu = TerminalMenu(e_options, title=f"Add Skill Category: {entry['category'] or 'New'}")
                    e_choice = e_menu.show()
                    if e_choice == 0: entry["category"] = input("Category: ")
                    elif e_choice == 1: entry["keywords"] = input_list("Keywords")
                    elif e_choice == 2 or e_choice is None: break
                public_data["skills"].append(entry)
            elif choice == 1:
                if not public_data["skills"]:
                    typer.echo("No skill categories to edit.")
                    continue
                s_options = [s["category"] for s in public_data["skills"]] + ["Back"]
                s_menu = TerminalMenu(s_options, title="Select Category to Edit")
                s_choice = s_menu.show()
                if s_choice is None or s_choice == len(public_data["skills"]):
                    continue
                entry = public_data["skills"][s_choice]
                while True:
                    e_options = ["Category Name", "Keywords", "Back"]
                    e_menu = TerminalMenu(e_options, title=f"Edit Skill Category: {entry['category']}")
                    e_choice = e_menu.show()
                    if e_choice == 0: entry["category"] = input("Category: ")
                    elif e_choice == 1: entry["keywords"] = input_list("Keywords")
                    elif e_choice == 2 or e_choice is None: break
            elif choice == 2:
                if not public_data["skills"]:
                    typer.echo("No skill categories to remove.")
                    continue
                s_options = [s["category"] for s in public_data["skills"]] + ["Back"]
                s_menu = TerminalMenu(s_options, title="Select Category to Remove")
                s_choice = s_menu.show()
                if s_choice is None or s_choice == len(public_data["skills"]):
                    continue
                public_data["skills"].pop(s_choice)
            elif choice == 3 or choice is None: break

    def edit_projects():
        while True:
            options = ["Add Project", "Edit Project", "Remove Project", "Back"]
            menu = TerminalMenu(options, title="Projects (Public Data)")
            choice = menu.show()
            if choice == 0:
                entry = {"name": "", "description": "", "url": "", "highlights": []}
                while True:
                    e_options = ["Project Name", "Description", "URL", "Highlights", "Back"]
                    e_menu = TerminalMenu(e_options, title=f"Add Project: {entry['name'] or 'New'}")
                    e_choice = e_menu.show()
                    if e_choice == 0: entry["name"] = input("Name: ")
                    elif e_choice == 1: entry["description"] = input("Description: ")
                    elif e_choice == 2: entry["url"] = input("URL: ")
                    elif e_choice == 3: entry["highlights"] = input_list("Highlights")
                    elif e_choice == 4 or e_choice is None: break
                public_data["projects"].append(entry)
            elif choice == 3 or choice is None: break
            else: typer.echo("Edit/Remove coming soon!")

    while True:
        main_options = ["Basics", "Work Experience (Public)", "Education (Public)", "Skills (Public)", "Projects (Public)", "Save and Exit", "Exit without Saving"]
        main_menu = TerminalMenu(main_options, title="Main Menu")
        main_choice = main_menu.show()

        if main_choice == 0:
            edit_basics()
        elif main_choice == 1:
            edit_work()
        elif main_choice == 2:
            edit_education()
        elif main_choice == 3:
            edit_skills()
        elif main_choice == 4:
            edit_projects()
        elif main_choice == 5:
            with open("draft_private.yaml", "w") as f:
                yaml.dump(private_data, f)
            with open("draft_public.yaml", "w") as f:
                yaml.dump(public_data, f)
            typer.echo("Saved interactive drafts to draft_private.yaml and draft_public.yaml")
            break
        elif main_choice == 6 or main_choice is None:
            break
        else:
            typer.echo("Feature coming soon!")

if __name__ == "__main__":
    app()
