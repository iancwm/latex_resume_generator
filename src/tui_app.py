"""
TUI Editor Application for LaTeX Resume Generator.

Provides a Textual-based TUI with split panes for editing resume data
and viewing live YAML preview.
"""

import copy
import yaml
import requests

from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer, Vertical
from textual.widgets import Header, Footer, Static

from src.session_manager import SessionManager
from src.undo_manager import UndoManager
from src.tui_widgets import (
    YAMLPreview,
    WorkEntryForm,
    WorkEntryChanged,
    EducationEntryForm,
    EducationChanged,
    BasicsForm,
    BasicsChanged,
    SkillCategoryForm,
    SkillsChanged,
    ProjectEntryForm,
    ProjectsChanged,
)


class ResumeEditorApp(App):
    """Main TUI application for the resume editor."""

    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+p", "toggle_preview", "Preview"),
        ("ctrl+z", "undo", "Undo"),
        ("ctrl+y", "redo", "Redo"),
        ("ctrl+1", "jump_basics", "Basics"),
        ("ctrl+2", "jump_work", "Work"),
        ("ctrl+3", "jump_education", "Education"),
        ("ctrl+4", "jump_skills", "Skills"),
        ("ctrl+5", "jump_projects", "Projects"),
        ("tab", "focus_next", "Next field"),
        ("shift+tab", "focus_previous", "Prev field"),
    ]

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 1fr 1fr;
        grid-rows: 1fr;
    }

    Header {
        dock: top;
    }

    Footer {
        dock: bottom;
    }

    #left-pane {
        background: $surface;
        border: solid $primary;
        padding: 1;
        overflow: auto;
    }

    #right-pane {
        background: $surface;
        border: solid $secondary;
        padding: 1;
    }

    .pane-title {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    /* Make input fields more visible when focused */
    Input {
        width: 100%;
    }

    Input:focus {
        background: $primary-darken-2;
        color: $text;
        text-style: reverse;
    }

    /* Ensure scrollable containers don't block focus */
    ScrollableContainer {
        scrollbar-gutter: stable;
    }
    """

    def __init__(self, session_name: str = "default"):
        """
        Initialize the Resume Editor App.

        Args:
            session_name: Name of the current editing session
        """
        super().__init__()
        self.session_name = session_name
        self.sub_title = f"Session: {session_name}"
        self.session_manager = SessionManager()
        self.undo_manager = UndoManager()
        self.current_data = {}

    def compose(self) -> ComposeResult:
        """Compose the TUI layout."""
        yield Header()
        yield Container(
            Vertical(
                Static("Personal Info (Basics)", classes="pane-title"),
                BasicsForm(id="basics-form"),
                Static("Education", classes="pane-title"),
                ScrollableContainer(id="education-forms-container"),
                Static("Work Experience", classes="pane-title"),
                ScrollableContainer(id="work-forms-container"),
                Static("Skills", classes="pane-title"),
                ScrollableContainer(id="skills-forms-container"),
                Static("Projects", classes="pane-title"),
                ScrollableContainer(id="projects-forms-container"),
                id="left-pane",
            ),
            Vertical(
                Static("YAML Preview", classes="pane-title"),
                YAMLPreview(id="yaml-preview"),
                id="right-pane",
            ),
            id="main-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load session data on mount and create work entry forms."""
        # Try to load existing session data
        loaded_data = self.session_manager.load(self.session_name)

        if loaded_data is not None:
            self.current_data = loaded_data
        else:
            # Initialize empty structure for new session
            self.current_data = {}

        # Set initial state for undo manager
        self.undo_manager.set_initial_state(copy.deepcopy(self.current_data))

        # Initialize basics form with current data
        self._update_basics_form()

        # Create education entry forms
        self._create_education_entry_forms()

        # Create work entry forms
        self._create_work_entry_forms()

        # Create skill category forms
        self._create_skill_category_forms()

        # Create project entry forms
        self._create_project_entry_forms()

        # Update YAML preview with current data
        self.update_yaml_preview()

        # Focus the first input field so user can start typing immediately
        self.call_after_refresh(self._focus_first_input)

    def _focus_first_input(self) -> None:
        """Focus the first input field in the basics form."""
        try:
            # Try to focus the first input in the basics form
            basics_form = self.query_one("#basics-form-container", ScrollableContainer)
            first_input = basics_form.query_one("Input")
            if first_input:
                first_input.focus()
        except Exception:
            # If basics form doesn't exist yet, try any input
            try:
                first_input = self.query_one("Input")
                if first_input:
                    first_input.focus()
            except Exception:
                pass  # No inputs available yet

    def _create_work_entry_forms(self) -> None:
        """Create WorkEntryForm widgets for each work entry in current_data."""
        try:
            container = self.query_one("#work-forms-container", ScrollableContainer)
            # Clear existing forms
            container.remove_children()

            # Get work entries from current_data
            work_entries = self.current_data.get("work", [])

            # If no work entries exist, create an empty one
            if not work_entries:
                work_entries = [{}]
                self.current_data["work"] = work_entries

            # Create a form for each work entry
            for i, entry in enumerate(work_entries):
                form = WorkEntryForm(entry=entry, entry_index=i, id=f"work-form-{i}")
                container.mount(form)

        except Exception:
            # Container may not be ready yet
            pass

    def _create_education_entry_forms(self) -> None:
        """Create EducationEntryForm widgets for each education entry in current_data."""
        try:
            container = self.query_one("#education-forms-container", ScrollableContainer)
            # Clear existing forms
            container.remove_children()

            # Get education entries from current_data
            education_entries = self.current_data.get("education", [])

            # If no education entries exist, create an empty one
            if not education_entries:
                education_entries = [{}]
                self.current_data["education"] = education_entries

            # Create a form for each education entry
            for i, entry in enumerate(education_entries):
                form = EducationEntryForm(entry=entry, entry_index=i, id=f"edu-form-{i}")
                container.mount(form)

        except Exception:
            # Container may not be ready yet
            pass

    def _create_skill_category_forms(self) -> None:
        """Create SkillCategoryForm widgets for each skill category in current_data."""
        try:
            container = self.query_one("#skills-forms-container", ScrollableContainer)
            # Clear existing forms
            container.remove_children()

            # Get skill categories from current_data
            skills_entries = self.current_data.get("skills", [])

            # If no skill entries exist, create an empty one
            if not skills_entries:
                skills_entries = [{}]
                self.current_data["skills"] = skills_entries

            # Create a form for each skill category
            for i, entry in enumerate(skills_entries):
                form = SkillCategoryForm(entry=entry, entry_index=i, id=f"skill-form-{i}")
                container.mount(form)

        except Exception:
            # Container may not be ready yet
            pass

    def _create_project_entry_forms(self) -> None:
        """Create ProjectEntryForm widgets for each project entry in current_data."""
        try:
            container = self.query_one("#projects-forms-container", ScrollableContainer)
            # Clear existing forms
            container.remove_children()

            # Get project entries from current_data
            projects_entries = self.current_data.get("projects", [])

            # If no project entries exist, create an empty one
            if not projects_entries:
                projects_entries = [{}]
                self.current_data["projects"] = projects_entries

            # Create a form for each project entry
            for i, entry in enumerate(projects_entries):
                form = ProjectEntryForm(entry=entry, entry_index=i, id=f"project-form-{i}")
                container.mount(form)

        except Exception:
            # Container may not be ready yet
            pass

    def _update_basics_form(self) -> None:
        """Update BasicsForm with current_data['basics']."""
        try:
            basics_form = self.query_one("#basics-form", BasicsForm)
            basics_data = self.current_data.get("basics", {})
            basics_form.basics = basics_data
            
            # Update all fields in the form
            location = basics_data.get("location", {})
            
            basics_form.query_one("#basics-name Input").value = basics_data.get("name", "")
            basics_form.query_one("#basics-email Input").value = basics_data.get("email", "")
            basics_form.query_one("#basics-phone Input").value = basics_data.get("phone", "")
            basics_form.query_one("#basics-city Input").value = location.get("city", "")
            basics_form.query_one("#basics-region Input").value = location.get("region", "")
            
        except Exception:
            # Widget may not be ready yet
            pass

    def on_basics_changed(self, message: BasicsChanged) -> None:
        """
        Handle basics form field changes.

        Args:
            message: BasicsChanged message containing field update info
        """
        # Push current state to undo manager before making changes
        self.undo_manager.push_state(copy.deepcopy(self.current_data))

        # Ensure basics dict exists
        if "basics" not in self.current_data:
            self.current_data["basics"] = {}

        basics = self.current_data["basics"]

        # Handle location fields specially (nested dict)
        if message.field_name in ("city", "region"):
            if "location" not in basics:
                basics["location"] = {}
            if message.value.strip():
                basics["location"][message.field_name] = message.value
            elif message.field_name in basics.get("location", {}):
                del basics["location"][message.field_name]
        else:
            # Handle top-level basics fields
            if message.value.strip():
                basics[message.field_name] = message.value
            elif message.field_name in basics:
                del basics[message.field_name]

        # Update YAML preview
        self.update_yaml_preview()

    def on_work_entry_changed(self, message: WorkEntryChanged) -> None:
        """
        Handle work entry field changes.

        Args:
            message: WorkEntryChanged message containing field update info
        """
        # Push current state to undo manager before making changes
        self.undo_manager.push_state(copy.deepcopy(self.current_data))

        # Ensure work list exists
        if "work" not in self.current_data:
            self.current_data["work"] = []

        # Ensure the entry exists in the list
        work_list = self.current_data["work"]
        while len(work_list) <= message.entry_index:
            work_list.append({})

        # Update the field in current_data
        entry = work_list[message.entry_index]

        # Map field names to YAML keys
        field_to_key = {
            "company": "company",
            "position": "position",
            "location": "location",
            "start_date": "startDate",
            "end_date": "endDate",
        }

        yaml_key = field_to_key.get(message.field_name, message.field_name)

        # Update or remove the field based on value
        if message.value.strip():
            entry[yaml_key] = message.value
        elif yaml_key in entry:
            del entry[yaml_key]

        # Update YAML preview
        self.update_yaml_preview()

    def on_education_entry_changed(self, message: EducationChanged) -> None:
        """
        Handle education entry field changes.

        Args:
            message: EducationChanged message containing field update info
        """
        # Push current state to undo manager before making changes
        self.undo_manager.push_state(copy.deepcopy(self.current_data))

        # Ensure education list exists
        if "education" not in self.current_data:
            self.current_data["education"] = []

        # Ensure the entry exists in the list
        education_list = self.current_data["education"]
        while len(education_list) <= message.entry_index:
            education_list.append({})

        # Update the field in current_data
        entry = education_list[message.entry_index]

        # Map field names to YAML keys
        field_to_key = {
            "institution": "institution",
            "area": "area",
            "location": "location",
            "start_date": "startDate",
            "end_date": "endDate",
            "score": "score",
        }

        yaml_key = field_to_key.get(message.field_name, message.field_name)

        # Update or remove the field based on value
        if message.value.strip():
            entry[yaml_key] = message.value
        elif yaml_key in entry:
            del entry[yaml_key]

        # Update YAML preview
        self.update_yaml_preview()

    def on_skills_changed(self, message: SkillsChanged) -> None:
        """
        Handle skill category field changes.

        Args:
            message: SkillsChanged message containing field update info
        """
        # Push current state to undo manager before making changes
        self.undo_manager.push_state(copy.deepcopy(self.current_data))

        # Ensure skills list exists
        if "skills" not in self.current_data:
            self.current_data["skills"] = []

        # Ensure the entry exists in the list
        skills_list = self.current_data["skills"]
        while len(skills_list) <= message.entry_index:
            skills_list.append({})

        # Update the field in current_data
        entry = skills_list[message.entry_index]

        # Map field names to YAML keys
        field_to_key = {
            "category": "category",
            "keywords": "keywords",
        }

        yaml_key = field_to_key.get(message.field_name, message.field_name)

        # Update or remove the field based on value
        if message.value.strip():
            # Special handling for keywords: convert comma-separated string to list
            if yaml_key == "keywords":
                keywords_list = [kw.strip() for kw in message.value.split(",") if kw.strip()]
                if keywords_list:
                    entry[yaml_key] = keywords_list
                elif yaml_key in entry:
                    del entry[yaml_key]
            else:
                entry[yaml_key] = message.value
        elif yaml_key in entry:
            del entry[yaml_key]

        # Update YAML preview
        self.update_yaml_preview()

    def on_projects_changed(self, message: ProjectsChanged) -> None:
        """
        Handle project entry field changes.

        Args:
            message: ProjectsChanged message containing field update info
        """
        # Push current state to undo manager before making changes
        self.undo_manager.push_state(copy.deepcopy(self.current_data))

        # Ensure projects list exists
        if "projects" not in self.current_data:
            self.current_data["projects"] = []

        # Ensure the entry exists in the list
        projects_list = self.current_data["projects"]
        while len(projects_list) <= message.entry_index:
            projects_list.append({})

        # Update the field in current_data
        entry = projects_list[message.entry_index]

        # Map field names to YAML keys
        field_to_key = {
            "name": "name",
            "description": "description",
            "url": "url",
            "highlights": "highlights",
        }

        yaml_key = field_to_key.get(message.field_name, message.field_name)

        # Update or remove the field based on value
        if message.value.strip():
            # Special handling for highlights: convert comma-separated string to list
            if yaml_key == "highlights":
                highlights_list = [h.strip() for h in message.value.split(",") if h.strip()]
                if highlights_list:
                    entry[yaml_key] = highlights_list
                elif yaml_key in entry:
                    del entry[yaml_key]
            else:
                entry[yaml_key] = message.value
        elif yaml_key in entry:
            del entry[yaml_key]

        # Update YAML preview
        self.update_yaml_preview()

    def update_yaml_preview(self) -> None:
        """
        Update the YAML preview panel with current_data.

        Converts current_data dict to YAML string and displays it
        in the YAMLPreview widget.
        """
        try:
            yaml_preview = self.query_one("#yaml-preview", YAMLPreview)
            yaml_content = yaml.dump(self.current_data, default_flow_style=False, sort_keys=False)
            yaml_preview.set_yaml(yaml_content)
        except Exception:
            # Widget may not be ready yet, silently ignore
            pass

    def save_session(self) -> None:
        """Save current session data using SessionManager."""
        self.session_manager.save(self.session_name, self.current_data)

    def compile_resume(self) -> None:
        """
        Compile resume by POSTing to preview server.

        Splits current_data into private (basics) and public (everything else)
        and sends to preview server /compile endpoint.
        Updates sub_title with compile status.
        """
        try:
            # Split into private/public
            private = {"basics": self.current_data.get("basics", {})}
            public = {k: v for k, v in self.current_data.items() if k != "basics"}

            resp = requests.post(
                "http://localhost:8000/compile",
                json={"private": private, "public": public},
                timeout=5
            )

            if resp.status_code == 200:
                self.sub_title = f"Session: {self.session_name} | Compiled ✓"
            else:
                self.sub_title = f"Session: {self.session_name} | Compile failed"
        except Exception:
            self.sub_title = f"Session: {self.session_name} | Server unavailable"

    def _trigger_compile(self) -> None:
        """Trigger compile by calling compile_resume."""
        self.compile_resume()

    def action_focus_next(self) -> None:
        """Focus the next focusable widget."""
        self.screen.focus_next()

    def action_focus_previous(self) -> None:
        """Focus the previous focusable widget."""
        self.screen.focus_previous()

    def action_save(self) -> None:
        """Save session and trigger compile."""
        self.save_session()
        self._trigger_compile()

    def action_toggle_preview(self) -> None:
        """Open preview in browser."""
        import webbrowser
        webbrowser.open("http://localhost:8000/preview")
        self.notify("Preview opened in browser")

    def action_undo(self) -> None:
        """Undo last edit."""
        previous_state = self.undo_manager.undo()
        if previous_state is not None:
            self.current_data = previous_state
            # Update all forms with the undone state
            self._update_basics_form()
            self._create_education_entry_forms()
            self._create_work_entry_forms()
            self._create_skill_category_forms()
            self._create_project_entry_forms()
            self.update_yaml_preview()
            self.notify("Undo successful")
        else:
            self.notify("Nothing to undo")

    def action_redo(self) -> None:
        """Redo last undone edit."""
        next_state = self.undo_manager.redo()
        if next_state is not None:
            self.current_data = next_state
            # Update all forms with the redone state
            self._update_basics_form()
            self._create_education_entry_forms()
            self._create_work_entry_forms()
            self._create_skill_category_forms()
            self._create_project_entry_forms()
            self.update_yaml_preview()
            self.notify("Redo successful")
        else:
            self.notify("Nothing to redo")

    def action_jump_basics(self) -> None:
        """Scroll to Basics section."""
        try:
            basics_form = self.query_one("#basics-form", BasicsForm)
            basics_form.scroll_visible()
            basics_form.focus()
            self.notify("Jumped to Basics section")
        except Exception:
            self.notify("Could not jump to Basics section")

    def action_jump_work(self) -> None:
        """Scroll to Work section."""
        try:
            container = self.query_one("#work-forms-container", ScrollableContainer)
            container.scroll_visible()
            # Focus first work form if available
            work_form = self.query_one("#work-form-0", WorkEntryForm)
            if work_form:
                work_form.focus()
            self.notify("Jumped to Work section")
        except Exception:
            self.notify("Could not jump to Work section")

    def action_jump_education(self) -> None:
        """Scroll to Education section."""
        try:
            container = self.query_one("#education-forms-container", ScrollableContainer)
            container.scroll_visible()
            # Focus first education form if available
            edu_form = self.query_one("#edu-form-0", EducationEntryForm)
            if edu_form:
                edu_form.focus()
            self.notify("Jumped to Education section")
        except Exception:
            self.notify("Could not jump to Education section")

    def action_jump_skills(self) -> None:
        """Scroll to Skills section."""
        try:
            container = self.query_one("#skills-forms-container", ScrollableContainer)
            container.scroll_visible()
            # Focus first skill form if available
            skill_form = self.query_one("#skill-form-0", SkillCategoryForm)
            if skill_form:
                skill_form.focus()
            self.notify("Jumped to Skills section")
        except Exception:
            self.notify("Could not jump to Skills section")

    def action_jump_projects(self) -> None:
        """Scroll to Projects section."""
        try:
            container = self.query_one("#projects-forms-container", ScrollableContainer)
            container.scroll_visible()
            # Focus first project form if available
            project_form = self.query_one("#project-form-0", ProjectEntryForm)
            if project_form:
                project_form.focus()
            self.notify("Jumped to Projects section")
        except Exception:
            self.notify("Could not jump to Projects section")


def run_editor(session_name: str = "default") -> None:
    """
    Run the resume editor TUI application.

    Args:
        session_name: Name of the editing session (displayed in header)
    """
    app = ResumeEditorApp(session_name=session_name)
    app.run()


if __name__ == "__main__":
    run_editor()
