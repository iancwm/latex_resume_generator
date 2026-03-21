import os
import re
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
            registry[doc_type][name] = {
                "path": file_path,
                "description": description
            }
    return registry


def get_default_template_name(doc_type: str) -> str:
    config = load_config()
    defaults = config.get("defaults", {})
    fallback_map = {
        "resume_template": "modern",
        "cover_letter_template": "standard"
    }
    config_key = f"{doc_type}_template"
    fallback = fallback_map.get(config_key)
    configured = defaults.get(config_key, fallback)
    registry = get_template_registry()
    if configured not in registry[doc_type]:
        return fallback
    return configured


def resolve_template_path(
    doc_type: str,
    template_name: str | None
) -> tuple[str, str]:
    registry = get_template_registry()
    selected = template_name or get_default_template_name(doc_type)
    templates = registry[doc_type]
    if selected not in templates:
        valid = ", ".join(sorted(templates.keys()))
        raise typer.BadParameter(
            f"Unknown {doc_type} template '{selected}'. Valid options: {valid}"
        )
    return selected, templates[selected]["path"]


@app.command()
def generate_resume(
    private: str = "inputs/private.yaml",
    public: str = "inputs/public.yaml",
    template_name: str | None = typer.Option(
        None, "--template-name", help="Resume template name."
    ),
    output: str = "dist/resume.tex",
    redacted: bool = False,
    compile: bool = typer.Option(False, "--compile", help="Compile to PDF.")
):
    selected_template, template_path = resolve_template_path(
        "resume", template_name
    )
    os.makedirs(os.path.dirname(output), exist_ok=True)
    engine_generate(
        private, public, template_path, output, redacted, compile=compile
    )
    print("Resume generated successfully.")


@app.command()
def generate_cover_letter(
    private: str = "inputs/private.yaml",
    public: str = "inputs/public.yaml",
    template_name: str | None = typer.Option(
        None, "--template-name", help="Cover letter template name."
    ),
    output: str = "dist/cover_letter.tex",
    redacted: bool = False,
    compile: bool = typer.Option(False, "--compile", help="Compile to PDF.")
):
    selected_template, template_path = resolve_template_path(
        "cover_letter", template_name
    )
    os.makedirs(os.path.dirname(output), exist_ok=True)
    engine_generate(
        private, public, template_path, output, redacted, compile=compile
    )
    print("Cover letter generated successfully.")


@app.command()
def list_templates():
    registry = get_template_registry()
    typer.echo(
        f"Resume templates (default: {get_default_template_name('resume')}):"
    )
    for name, data in registry["resume"].items():
        typer.echo(f"  - {name}: {data['description']}")
    typer.echo(
        f"\nCover letter templates (default: "
        f"{get_default_template_name('cover_letter')}):"
    )
    for name, data in registry["cover_letter"].items():
        typer.echo(f"  - {name}: {data['description']}")


def deep_merge(target: dict, source: dict):
    """
    Recursively merges source dict into target dict.
    """
    for key, value in source.items():
        if (
            isinstance(value, dict) and
            key in target and
            isinstance(target[key], dict)
        ):
            deep_merge(target[key], value)
        else:
            target[key] = value


def validate_required(value: str, field_name: str) -> bool:
    """
    Validates that a string value is not empty.

    Args:
        value: The string to validate.
        field_name: The name of the field (for error messaging).

    Returns:
        True if valid, False otherwise.
    """
    if not value or not value.strip():
        typer.echo(f"Error: {field_name} cannot be empty.")
        return False
    return True


def validate_date(value: str) -> bool:
    """
    Validates that a string follows YYYY-MM or 'Present' format.

    Args:
        value: The string to validate.

    Returns:
        True if valid, False otherwise.
    """
    if value == "Present":
        return True
    if re.match(r"^\d{4}-(0[1-9]|1[0-2])$", value):
        return True
    typer.echo("Error: Invalid date format. Use YYYY-MM or 'Present'.")
    return False


def input_with_validation(
    prompt: str,
    validator: callable = None,
    field_name: str | None = None
) -> str:
    """
    Prompts the user for input and validates it.

    Args:
        prompt: The prompt message.
        validator: An optional validation function.
        field_name: An optional field name for the validator.

    Returns:
        The validated input string.
    """
    while True:
        value = input(f"{prompt}: ")
        if validator:
            if field_name:
                if validator(value, field_name):
                    return value
            else:
                if validator(value):
                    return value
        else:
            return value


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
                deep_merge(private_data, existing_private)

    if os.path.exists("inputs/public.yaml"):
        with open("inputs/public.yaml", "r") as f:
            existing_public = yaml.safe_load(f)
            if isinstance(existing_public, dict):
                deep_merge(public_data, existing_public)

    def input_list(prompt_msg: str) -> list[str]:
        items = []
        typer.echo(f"{prompt_msg} (Enter empty line to finish)")
        while True:
            item = input("> ")
            if not item:
                break
            items.append(item)

        if items:
            has_period = [i.endswith(".") for i in items]
            if any(has_period) and not all(has_period):
                typer.echo("Warning: Inconsistent punctuation detected.")
                msg = "Would you like to add periods to all items? (y/n)"
                choice = input(f"{msg}: ").lower()
                if choice == "y":
                    items = [i if i.endswith(".") else i + "." for i in items]
                else:
                    msg = "Would you like to remove periods from all? (y/n)"
                    choice = input(f"{msg}: ").lower()
                    if choice == "y":
                        items = [
                            i[:-1] if i.endswith(".") else i for i in items
                        ]
        return items

    def edit_basics():
        while True:
            options = [
                "Name", "Email", "Phone", "Location (City)",
                "Location (Region)", "Back"
            ]
            menu = TerminalMenu(options, title="Basics (Private Data)")
            choice = menu.show()
            if choice == 0:
                private_data["basics"]["name"] = input_with_validation(
                    "Name", validate_required, "Name"
                )
            elif choice == 1:
                private_data["basics"]["email"] = input_with_validation(
                    "Email", validate_required, "Email"
                )
            elif choice == 2:
                private_data["basics"]["phone"] = input("Phone: ")
            elif choice == 3:
                private_data["basics"]["location"]["city"] = input("City: ")
            elif choice == 4:
                private_data["basics"]["location"]["region"] = input(
                    "Region: "
                )
            elif choice == 5 or choice is None:
                break

    def edit_work():
        while True:
            options = ["Add Entry", "Edit Entry", "Remove Entry", "Back"]
            menu = TerminalMenu(options, title="Work Experience (Public Data)")
            choice = menu.show()
            if choice == 0:
                entry = {
                    "company": "", "position": "", "location": "",
                    "startDate": "", "endDate": "", "summary": []
                }
                while True:
                    e_options = [
                        "Company", "Position", "Location",
                        "Start Date", "End Date", "Summary", "Back"
                    ]
                    e_menu = TerminalMenu(
                        e_options,
                        title=f"Add Work Entry: {entry['company'] or 'New'}"
                    )
                    e_choice = e_menu.show()
                    if e_choice == 0:
                        entry["company"] = input_with_validation(
                            "Company", validate_required, "Company"
                        )
                    elif e_choice == 1:
                        entry["position"] = input_with_validation(
                            "Position", validate_required, "Position"
                        )
                    elif e_choice == 2:
                        entry["location"] = input("Location: ")
                    elif e_choice == 3:
                        entry["startDate"] = input_with_validation(
                            "Start Date (YYYY-MM)", validate_date
                        )
                    elif e_choice == 4:
                        entry["endDate"] = input_with_validation(
                            "End Date (YYYY-MM/Present)", validate_date
                        )
                    elif e_choice == 5:
                        entry["summary"] = input_list("Summary Points")
                    elif e_choice == 6 or e_choice is None:
                        break
                public_data["work"].append(entry)
            elif choice == 3 or choice is None:
                break
            else:
                typer.echo("Edit/Remove coming soon!")

    def edit_education():
        while True:
            options = ["Add Entry", "Edit Entry", "Remove Entry", "Back"]
            menu = TerminalMenu(options, title="Education (Public Data)")
            choice = menu.show()
            if choice == 0:
                entry = {
                    "institution": "", "area": "", "location": "",
                    "startDate": "", "endDate": "", "score": "",
                    "honors": [], "courses": []
                }
                while True:
                    e_options = [
                        "Institution", "Area", "Location", "Start Date",
                        "End Date", "Score/GPA", "Honors", "Courses", "Back"
                    ]
                    e_menu = TerminalMenu(
                        e_options,
                        title=f"Add Education Entry: "
                        f"{entry['institution'] or 'New'}"
                    )
                    e_choice = e_menu.show()
                    if e_choice == 0:
                        entry["institution"] = input_with_validation(
                            "Institution", validate_required, "Institution"
                        )
                    elif e_choice == 1:
                        entry["area"] = input_with_validation(
                            "Area of Study", validate_required, "Area of Study"
                        )
                    elif e_choice == 2:
                        entry["location"] = input("Location: ")
                    elif e_choice == 3:
                        entry["startDate"] = input_with_validation(
                            "Start Date (YYYY-MM)", validate_date
                        )
                    elif e_choice == 4:
                        entry["endDate"] = input_with_validation(
                            "End Date (YYYY-MM)", validate_date
                        )
                    elif e_choice == 5:
                        entry["score"] = input("Score/GPA: ")
                    elif e_choice == 6:
                        entry["honors"] = input_list("Honors")
                    elif e_choice == 7:
                        entry["courses"] = input_list("Courses")
                    elif e_choice == 8 or e_choice is None:
                        break
                public_data["education"].append(entry)
            elif choice == 3 or choice is None:
                break
            else:
                typer.echo("Edit/Remove coming soon!")

    def edit_skills():
        while True:
            options = [
                "Add Category", "Edit Category", "Remove Category", "Back"
            ]
            menu = TerminalMenu(options, title="Skills (Public Data)")
            choice = menu.show()
            if choice == 0:
                entry = {"category": "", "keywords": []}
                while True:
                    e_options = ["Category Name", "Keywords", "Back"]
                    e_menu = TerminalMenu(
                        e_options,
                        title=f"Add Skill Category: "
                        f"{entry['category'] or 'New'}"
                    )
                    e_choice = e_menu.show()
                    if e_choice == 0:
                        entry["category"] = input_with_validation(
                            "Category", validate_required, "Category"
                        )
                    elif e_choice == 1:
                        entry["keywords"] = input_list("Keywords")
                    elif e_choice == 2 or e_choice is None:
                        break
                public_data["skills"].append(entry)
            elif choice == 1:
                if not public_data["skills"]:
                    typer.echo("No skill categories to edit.")
                    continue
                s_options = [s["category"] for s in public_data["skills"]] + [
                    "Back"
                ]
                s_menu = TerminalMenu(
                    s_options, title="Select Category to Edit"
                )
                s_choice = s_menu.show()
                if s_choice is None or s_choice == len(public_data["skills"]):
                    continue
                entry = public_data["skills"][s_choice]
                while True:
                    e_options = ["Category Name", "Keywords", "Back"]
                    e_menu = TerminalMenu(
                        e_options,
                        title=f"Edit Skill Category: {entry['category']}"
                    )
                    e_choice = e_menu.show()
                    if e_choice == 0:
                        entry["category"] = input_with_validation(
                            "Category", validate_required, "Category"
                        )
                    elif e_choice == 1:
                        entry["keywords"] = input_list("Keywords")
                    elif e_choice == 2 or e_choice is None:
                        break
            elif choice == 2:
                if not public_data["skills"]:
                    typer.echo("No skill categories to remove.")
                    continue
                s_options = [s["category"] for s in public_data["skills"]] + [
                    "Back"
                ]
                s_menu = TerminalMenu(
                    s_options, title="Select Category to Remove"
                )
                s_choice = s_menu.show()
                if s_choice is None or s_choice == len(public_data["skills"]):
                    continue
                public_data["skills"].pop(s_choice)
            elif choice == 3 or choice is None:
                break

    def edit_projects():
        while True:
            options = ["Add Project", "Edit Project", "Remove Project", "Back"]
            menu = TerminalMenu(options, title="Projects (Public Data)")
            choice = menu.show()
            if choice == 0:
                entry = {
                    "name": "", "description": "", "url": "", "highlights": []
                }
                while True:
                    e_options = [
                        "Project Name", "Description", "URL",
                        "Highlights", "Back"
                    ]
                    e_menu = TerminalMenu(
                        e_options,
                        title=f"Add Project: {entry['name'] or 'New'}"
                    )
                    e_choice = e_menu.show()
                    if e_choice == 0:
                        entry["name"] = input_with_validation(
                            "Name", validate_required, "Project Name"
                        )
                    elif e_choice == 1:
                        entry["description"] = input("Description: ")
                    elif e_choice == 2:
                        entry["url"] = input("URL: ")
                    elif e_choice == 3:
                        entry["highlights"] = input_list("Highlights")
                    elif e_choice == 4 or e_choice is None:
                        break
                public_data["projects"].append(entry)
            elif choice == 1:
                if not public_data["projects"]:
                    typer.echo("No projects to edit.")
                    continue
                p_options = [p["name"] for p in public_data["projects"]] + [
                    "Back"
                ]
                p_menu = TerminalMenu(
                    p_options, title="Select Project to Edit"
                )
                p_choice = p_menu.show()
                if p_choice is None or \
                   p_choice == len(public_data["projects"]):
                    continue
                entry = public_data["projects"][p_choice]
                while True:
                    e_options = [
                        "Project Name", "Description", "URL",
                        "Highlights", "Back"
                    ]
                    e_menu = TerminalMenu(
                        e_options,
                        title=f"Edit Project: {entry['name']}"
                    )
                    e_choice = e_menu.show()
                    if e_choice == 0:
                        entry["name"] = input_with_validation(
                            "Name", validate_required, "Project Name"
                        )
                    elif e_choice == 1:
                        entry["description"] = input("Description: ")
                    elif e_choice == 2:
                        entry["url"] = input("URL: ")
                    elif e_choice == 3:
                        entry["highlights"] = input_list("Highlights")
                    elif e_choice == 4 or e_choice is None:
                        break
            elif choice == 2:
                if not public_data["projects"]:
                    typer.echo("No projects to remove.")
                    continue
                p_options = [p["name"] for p in public_data["projects"]] + [
                    "Back"
                ]
                p_menu = TerminalMenu(
                    p_options, title="Select Project to Remove"
                )
                p_choice = p_menu.show()
                if p_choice is None or \
                   p_choice == len(public_data["projects"]):
                    continue
                public_data["projects"].pop(p_choice)
            elif choice == 3 or choice is None:
                break

    while True:
        main_options = [
            "Basics", "Work Experience (Public)", "Education (Public)",
            "Skills (Public)", "Projects (Public)", "Save and Exit",
            "Exit without Saving"
        ]
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
            os.makedirs("drafts", exist_ok=True)
            name = private_data.get("basics", {}).get("name", "anonymous")
            first_name = name.split()[0].lower() if name else "anonymous"
            private_file = f"drafts/private_{first_name}.yaml"
            public_file = f"drafts/public_{first_name}.yaml"

            with open(private_file, "w") as f:
                yaml.dump(private_data, f)
            with open(public_file, "w") as f:
                yaml.dump(public_data, f)
            typer.echo(
                f"Saved interactive drafts to {private_file} and {public_file}"
            )
            break
        elif main_choice == 6 or main_choice is None:
            break
        else:
            typer.echo("Feature coming soon!")


if __name__ == "__main__":
    app()
