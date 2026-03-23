"""
Custom Textual widgets for the LaTeX Resume Generator TUI Editor.

Provides reusable widgets for form editing and YAML preview.
"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Input, Label, Static, TextArea
from textual.widget import Widget


class FormField(Widget):
    """
    A labeled input field widget for form editing.

    Provides a label and input field with get_value/set_value methods
    for easy data access.
    """

    DEFAULT_CSS = """
    FormField {
        layout: vertical;
        margin-bottom: 1;
    }

    FormField > Label {
        text-style: bold;
        margin-bottom: 0;
    }

    FormField > Input {
        width: 100%;
    }
    """

    def __init__(
        self,
        field_name: str,
        label: str,
        value: str = "",
        placeholder: str = "",
        id: str | None = None,
    ):
        """
        Initialize a FormField widget.

        Args:
            field_name: Internal name/identifier for the field
            label: Display label for the field
            value: Initial value for the input
            placeholder: Placeholder text for the input
            id: Optional widget ID
        """
        super().__init__(id=id)
        self.field_name = field_name
        self.label_text = label
        self._initial_value = value
        self._placeholder = placeholder

    def compose(self) -> ComposeResult:
        """Compose the form field layout."""
        yield Label(self.label_text, id=f"label-{self.field_name}")
        yield Input(
            value=self._initial_value,
            placeholder=self._placeholder,
            id=f"input-{self.field_name}",
        )

    def get_value(self) -> str:
        """
        Get the current value of the input field.

        Returns:
            The current text value of the input field
        """
        input_widget = self.query_one(f"#input-{self.field_name}", Input)
        return input_widget.value

    def set_value(self, value: str) -> None:
        """
        Set the value of the input field.

        Args:
            value: The value to set
        """
        input_widget = self.query_one(f"#input-{self.field_name}", Input)
        input_widget.value = value


class YAMLPreview(TextArea):
    """
    A syntax-highlighted YAML preview widget.

    Extends TextArea with YAML syntax highlighting and a convenient
    set_yaml method for updating the displayed content.
    """

    DEFAULT_CSS = """
    YAMLPreview {
        height: 100%;
        width: 100%;
    }

    YAMLPreview TextArea {
        background: $surface;
    }
    """

    def __init__(self, id: str | None = None):
        """
        Initialize the YAML Preview widget.

        Args:
            id: Optional widget ID
        """
        super().__init__(id=id, language="yaml", read_only=True)

    def set_yaml(self, yaml_content: str) -> None:
        """
        Set the YAML content to display.

        Args:
            yaml_content: The YAML content to display in the preview
        """
        self.text = yaml_content


class SectionChanged(Message):
    """
    Message posted when a section tab is changed.

    Attributes:
        section_index: The index of the newly selected section (0-4)
        section_name: The name of the newly selected section
    """

    def __init__(self, section_index: int, section_name: str):
        """
        Initialize a SectionChanged message.

        Args:
            section_index: The index of the selected section
            section_name: The name of the selected section
        """
        super().__init__()
        self.section_index = section_index
        self.section_name = section_name


class SectionTabs(Static):
    """
    Tab navigation widget for switching between resume sections.

    Provides keyboard bindings (Ctrl+1 through Ctrl+5) for quick
    section navigation. Posts SectionChanged messages when the
    active tab changes.

    Sections:
        1. Personal Info
        2. Education
        3. Experience
        4. Skills
        5. Projects
    """

    BINDINGS = [
        Binding("ctrl+1", "select_section(0)", "Section 1", show=False),
        Binding("ctrl+2", "select_section(1)", "Section 2", show=False),
        Binding("ctrl+3", "select_section(2)", "Section 3", show=False),
        Binding("ctrl+4", "select_section(3)", "Section 4", show=False),
        Binding("ctrl+5", "select_section(4)", "Section 5", show=False),
    ]

    SECTIONS = [
        ("Personal", "Personal Info"),
        ("Education", "Education"),
        ("Experience", "Experience"),
        ("Skills", "Skills"),
        ("Projects", "Projects"),
    ]

    DEFAULT_CSS = """
    SectionTabs {
        height: auto;
        margin-bottom: 1;
    }

    SectionTabs .tabs-container {
        layout: horizontal;
        height: auto;
    }

    SectionTabs .tab {
        padding: 0 2;
        background: $surface;
        text-style: bold;
    }

    SectionTabs .tab-active {
        background: $primary;
        color: $text;
    }

    SectionTabs .tab-inactive {
        background: $surface;
        color: $text-muted;
    }
    """

    def __init__(self, id: str | None = None):
        """
        Initialize the SectionTabs widget.

        Args:
            id: Optional widget ID
        """
        super().__init__(id=id)
        self._active_section = 0

    def compose(self) -> ComposeResult:
        """Compose the tabs layout."""
        with Horizontal(classes="tabs-container"):
            for i, (key, name) in enumerate(self.SECTIONS):
                tab_classes = ["tab"]
                tab_classes.append("tab-active" if i == 0 else "tab-inactive")
                yield Static(f"[{i + 1}] {key}", classes=" ".join(tab_classes), id=f"tab-{i}")

    def on_mount(self) -> None:
        """Handle widget mount."""
        self._update_tab_styles()

    def _update_tab_styles(self) -> None:
        """Update the visual style of tabs based on active section."""
        for i in range(len(self.SECTIONS)):
            tab = self.query_one(f"#tab-{i}", Static)
            tab.remove_class("tab-active")
            tab.remove_class("tab-inactive")
            if i == self._active_section:
                tab.add_class("tab-active")
            else:
                tab.add_class("tab-inactive")

    def action_select_section(self, section_index: int) -> None:
        """
        Select a section by index.

        Args:
            section_index: The index of the section to select (0-4)
        """
        if 0 <= section_index < len(self.SECTIONS):
            self._active_section = section_index
            self._update_tab_styles()
            section_key, section_name = self.SECTIONS[section_index]
            self.post_message(SectionChanged(section_index, section_name))

    @property
    def active_section(self) -> int:
        """Get the currently active section index."""
        return self._active_section

    @property
    def active_section_name(self) -> str:
        """Get the name of the currently active section."""
        return self.SECTIONS[self._active_section][1]
