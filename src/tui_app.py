"""
TUI Editor Application for LaTeX Resume Generator.

Provides a Textual-based TUI with split panes for editing resume data
and viewing live YAML preview.
"""

import yaml

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static

from src.session_manager import SessionManager
from src.tui_widgets import YAMLPreview


class ResumeEditorApp(App):
    """Main TUI application for the resume editor."""

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
                Static("Form Editor", classes="pane-title"),
                Static("[Form Editor - Coming Soon]", id="form-editor-content"),
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
        """Load session data on mount."""
        # Try to load existing session data
        loaded_data = self.session_manager.load(self.session_name)

        if loaded_data is not None:
            self.current_data = loaded_data
        else:
            # Initialize empty structure for new session
            self.current_data = {}

        # Update YAML preview with current data
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
