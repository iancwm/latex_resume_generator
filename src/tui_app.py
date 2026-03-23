"""
TUI Editor Application for LaTeX Resume Generator.

Provides a Textual-based TUI with split panes for editing resume data
and viewing live YAML preview.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static


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
                Static("[YAML Preview - Coming Soon]", id="yaml-preview-content"),
                id="right-pane",
            ),
            id="main-container",
        )
        yield Footer()


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
