"""
TUI Editor Application for LaTeX Resume Generator.

Provides a Textual-based TUI with split panes for editing resume data
and viewing live YAML preview.
"""

import yaml
import requests

from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer, Vertical
from textual.widgets import Header, Footer, Static

from src.session_manager import SessionManager
from src.tui_widgets import YAMLPreview, WorkEntryForm, WorkEntryChanged, BasicsForm, BasicsChanged


class ResumeEditorApp(App):
    """Main TUI application for the resume editor."""

    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("ctrl+q", "quit", "Quit"),
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
        self.current_data = {}

    def compose(self) -> ComposeResult:
        """Compose the TUI layout."""
        yield Header()
        yield Container(
            Vertical(
                Static("Personal Info (Basics)", classes="pane-title"),
                BasicsForm(id="basics-form"),
                Static("Work Experience", classes="pane-title"),
                ScrollableContainer(id="work-forms-container"),
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

        # Initialize basics form with current data
        self._update_basics_form()

        # Create work entry forms
        self._create_work_entry_forms()

        # Update YAML preview with current data
        self.update_yaml_preview()

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

    def action_save(self) -> None:
        """Save session and trigger compile."""
        self.save_session()
        self._trigger_compile()


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
