"""
Custom Textual widgets for the LaTeX Resume Generator TUI Editor.

Provides reusable widgets for form editing and YAML preview.
"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.widgets import Button, Input, Label, Static, TextArea
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
        # Parent widget should not take focus, only the Input should
        self.can_focus = False

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


class BasicsChanged(Message):
    """
    Message posted when a basics form field is changed.

    Attributes:
        field_name: The name of the field that changed
        value: The new value of the field
    """

    def __init__(
        self,
        field_name: str,
        value: str,
    ):
        """
        Initialize a BasicsChanged message.

        Args:
            field_name: The name of the field that changed
            value: The new value of the field
        """
        super().__init__()
        self.field_name = field_name
        self.value = value


class WorkEntryChanged(Message):
    """
    Message posted when a work entry form field is changed.

    Attributes:
        entry_index: The index of the work entry being edited
        field_name: The name of the field that changed
        value: The new value of the field
        is_valid: Whether the new value passes validation
    """

    def __init__(
        self,
        entry_index: int,
        field_name: str,
        value: str,
        is_valid: bool = True,
    ):
        """
        Initialize a WorkEntryChanged message.

        Args:
            entry_index: The index of the work entry being edited
            field_name: The name of the field that changed
            value: The new value of the field
            is_valid: Whether the value passes validation
        """
        super().__init__()
        self.entry_index = entry_index
        self.field_name = field_name
        self.value = value
        self.is_valid = is_valid


class EducationChanged(Message):
    """
    Message posted when an education entry form field is changed.

    Attributes:
        entry_index: The index of the education entry being edited
        field_name: The name of the field that changed
        value: The new value of the field
        is_valid: Whether the new value passes validation
    """

    def __init__(
        self,
        entry_index: int,
        field_name: str,
        value: str,
        is_valid: bool = True,
    ):
        """
        Initialize an EducationChanged message.

        Args:
            entry_index: The index of the education entry being edited
            field_name: The name of the field that changed
            value: The new value of the field
            is_valid: Whether the value passes validation
        """
        super().__init__()
        self.entry_index = entry_index
        self.field_name = field_name
        self.value = value
        self.is_valid = is_valid


class SkillsChanged(Message):
    """
    Message posted when a skill category form field is changed.

    Attributes:
        entry_index: The index of the skill category being edited
        field_name: The name of the field that changed
        value: The new value of the field
        is_valid: Whether the new value passes validation
    """

    def __init__(
        self,
        entry_index: int,
        field_name: str,
        value: str,
        is_valid: bool = True,
    ):
        """
        Initialize a SkillsChanged message.

        Args:
            entry_index: The index of the skill category being edited
            field_name: The name of the field that changed
            value: The new value of the field
            is_valid: Whether the value passes validation
        """
        super().__init__()
        self.entry_index = entry_index
        self.field_name = field_name
        self.value = value
        self.is_valid = is_valid


class ProjectsChanged(Message):
    """
    Message posted when a project entry form field is changed.

    Attributes:
        entry_index: The index of the project entry being edited
        field_name: The name of the field that changed
        value: The new value of the field
        is_valid: Whether the new value passes validation
    """

    def __init__(
        self,
        entry_index: int,
        field_name: str,
        value: str,
        is_valid: bool = True,
    ):
        """
        Initialize a ProjectsChanged message.

        Args:
            entry_index: The index of the project entry being edited
            field_name: The name of the field that changed
            value: The new value of the field
            is_valid: Whether the value passes validation
        """
        super().__init__()
        self.entry_index = entry_index
        self.field_name = field_name
        self.value = value
        self.is_valid = is_valid


class WorkEntryForm(Container):
    """
    Form for editing a single work experience entry.

    Provides labeled input fields for all work entry attributes
    with validation support.
    """

    DEFAULT_CSS = """
    WorkEntryForm {
        layout: vertical;
        padding: 1;
        margin-bottom: 1;
        background: $surface;
        border: solid $primary;
    }

    WorkEntryForm .form-row {
        layout: horizontal;
        margin-bottom: 1;
    }

    WorkEntryForm .form-row FormField {
        width: 1fr;
        margin-right: 1;
        margin-bottom: 0;
    }

    WorkEntryForm .form-row FormField:last-child {
        margin-right: 0;
    }

    WorkEntryForm .error-message {
        color: $error;
        text-style: italic;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        entry: dict = None,
        entry_index: int = 0,
        **kwargs,
    ):
        """
        Initialize a WorkEntryForm widget.

        Args:
            entry: Dictionary containing work entry data
            entry_index: Index of this entry in the work list
            **kwargs: Additional keyword arguments for Container
        """
        super().__init__(**kwargs)
        self.entry = entry or {}
        self.entry_index = entry_index
        self._validation_errors = {}
        # Container should not take focus, only child Inputs should
        self.can_focus = False

    def compose(self) -> ComposeResult:
        """Compose the work entry form layout."""
        # First row: Company and Position
        with Horizontal(classes="form-row"):
            yield FormField(
                field_name="company",
                label="Company",
                value=self.entry.get("company", ""),
                placeholder="e.g., Acme Corp",
                id=f"work-{self.entry_index}-company",
            )
            yield FormField(
                field_name="position",
                label="Position",
                value=self.entry.get("position", ""),
                placeholder="e.g., Software Engineer",
                id=f"work-{self.entry_index}-position",
            )

        # Second row: Location
        yield FormField(
            field_name="location",
            label="Location",
            value=self.entry.get("location", ""),
            placeholder="e.g., San Francisco, CA",
            id=f"work-{self.entry_index}-location",
        )

        # Third row: Start Date and End Date
        with Horizontal(classes="form-row"):
            yield FormField(
                field_name="start_date",
                label="Start Date",
                value=self.entry.get("startDate", ""),
                placeholder="YYYY-MM",
                id=f"work-{self.entry_index}-start_date",
            )
            yield FormField(
                field_name="end_date",
                label="End Date",
                value=self.entry.get("endDate", ""),
                placeholder="YYYY-MM or Present",
                id=f"work-{self.entry_index}-end_date",
            )

        # Error message display (hidden by default)
        yield Static("", id=f"work-{self.entry_index}-errors", classes="error-message")

    def on_mount(self) -> None:
        """Handle widget mount."""
        self._update_error_display()

    def _validate_field(self, field_name: str, value: str) -> bool:
        """
        Validate a field value.

        Args:
            field_name: Name of the field to validate
            value: Value to validate

        Returns:
            True if valid, False otherwise
        """
        from src.validators import validate_required, validate_date

        # Company and Position are required fields
        if field_name in ("company", "position"):
            return validate_required(value, field_name)

        # Date fields need date validation if not empty
        if field_name in ("start_date", "end_date") and value.strip():
            return validate_date(value)

        # Location is optional
        return True

    def _update_error_display(self) -> None:
        """Update the error message display."""
        try:
            error_widget = self.query_one(f"#work-{self.entry_index}-errors", Static)
            if self._validation_errors:
                errors = list(self._validation_errors.values())
                error_widget.update(" • ".join(errors))
                error_widget.display = True
            else:
                error_widget.display = False
        except Exception:
            # Widget may not be ready yet
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Handle input field changes.

        Args:
            event: Input changed event
        """
        # Extract field name from input ID
        input_id = event.input.id
        if not input_id or not input_id.startswith(f"work-{self.entry_index}-"):
            return

        field_name = input_id.replace(f"work-{self.entry_index}-", "")
        value = event.value

        # Validate the field
        is_valid = self._validate_field(field_name, value)

        # Update validation errors
        if is_valid and field_name in self._validation_errors:
            del self._validation_errors[field_name]
        elif not is_valid:
            if field_name in ("start_date", "end_date"):
                self._validation_errors[field_name] = f"Invalid date format for {field_name.replace('_', ' ')}"
            else:
                self._validation_errors[field_name] = f"{field_name.replace('_', ' ').title()} is required"

        self._update_error_display()

        # Post message to notify parent of the change
        self.post_message(
            WorkEntryChanged(
                entry_index=self.entry_index,
                field_name=field_name,
                value=value,
                is_valid=is_valid,
            )
        )


class EducationEntryForm(Container):
    """
    Form for editing a single education entry.

    Provides labeled input fields for all education entry attributes
    with validation support.
    """

    DEFAULT_CSS = """
    EducationEntryForm {
        layout: vertical;
        padding: 1;
        margin-bottom: 1;
        background: $surface;
        border: solid $primary;
    }

    EducationEntryForm .form-row {
        layout: horizontal;
        margin-bottom: 1;
    }

    EducationEntryForm .form-row FormField {
        width: 1fr;
        margin-right: 1;
        margin-bottom: 0;
    }

    EducationEntryForm .form-row FormField:last-child {
        margin-right: 0;
    }

    EducationEntryForm .error-message {
        color: $error;
        text-style: italic;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        entry: dict = None,
        entry_index: int = 0,
        **kwargs,
    ):
        """
        Initialize an EducationEntryForm widget.

        Args:
            entry: Dictionary containing education entry data
            entry_index: Index of this entry in the education list
            **kwargs: Additional keyword arguments for Container
        """
        super().__init__(**kwargs)
        self.entry = entry or {}
        self.entry_index = entry_index
        self._validation_errors = {}
        # Container should not take focus, only child Inputs should
        self.can_focus = False

    def compose(self) -> ComposeResult:
        """Compose the education entry form layout."""
        # First row: Institution and Area of Study
        with Horizontal(classes="form-row"):
            yield FormField(
                field_name="institution",
                label="Institution",
                value=self.entry.get("institution", ""),
                placeholder="e.g., University of California",
                id=f"edu-{self.entry_index}-institution",
            )
            yield FormField(
                field_name="area",
                label="Area of Study",
                value=self.entry.get("area", ""),
                placeholder="e.g., Computer Science",
                id=f"edu-{self.entry_index}-area",
            )

        # Second row: Location
        yield FormField(
            field_name="location",
            label="Location",
            value=self.entry.get("location", ""),
            placeholder="e.g., Berkeley, CA",
            id=f"edu-{self.entry_index}-location",
        )

        # Third row: Start Date and End Date
        with Horizontal(classes="form-row"):
            yield FormField(
                field_name="start_date",
                label="Start Date",
                value=self.entry.get("startDate", ""),
                placeholder="YYYY-MM",
                id=f"edu-{self.entry_index}-start_date",
            )
            yield FormField(
                field_name="end_date",
                label="End Date",
                value=self.entry.get("endDate", ""),
                placeholder="YYYY-MM or Present",
                id=f"edu-{self.entry_index}-end_date",
            )

        # Fourth row: Score/GPA
        yield FormField(
            field_name="score",
            label="Score/GPA",
            value=self.entry.get("score", ""),
            placeholder="e.g., 3.8/4.0 or 3.8 GPA",
            id=f"edu-{self.entry_index}-score",
        )

        # Error message display (hidden by default)
        yield Static("", id=f"edu-{self.entry_index}-errors", classes="error-message")

    def on_mount(self) -> None:
        """Handle widget mount."""
        self._update_error_display()

    def _validate_field(self, field_name: str, value: str) -> bool:
        """
        Validate a field value.

        Args:
            field_name: Name of the field to validate
            value: Value to validate

        Returns:
            True if valid, False otherwise
        """
        from src.validators import validate_required, validate_date

        # Institution and Area are required fields
        if field_name in ("institution", "area"):
            return validate_required(value, field_name)

        # Date fields need date validation if not empty
        if field_name in ("start_date", "end_date") and value.strip():
            return validate_date(value)

        # Location and Score are optional
        return True

    def _update_error_display(self) -> None:
        """Update the error message display."""
        try:
            error_widget = self.query_one(f"#edu-{self.entry_index}-errors", Static)
            if self._validation_errors:
                errors = list(self._validation_errors.values())
                error_widget.update(" • ".join(errors))
                error_widget.display = True
            else:
                error_widget.display = False
        except Exception:
            # Widget may not be ready yet
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Handle input field changes.

        Args:
            event: Input changed event
        """
        # Extract field name from input ID
        input_id = event.input.id
        if not input_id or not input_id.startswith(f"edu-{self.entry_index}-"):
            return

        field_name = input_id.replace(f"edu-{self.entry_index}-", "")
        value = event.value

        # Validate the field
        is_valid = self._validate_field(field_name, value)

        # Update validation errors
        if is_valid and field_name in self._validation_errors:
            del self._validation_errors[field_name]
        elif not is_valid:
            if field_name in ("start_date", "end_date"):
                self._validation_errors[field_name] = f"Invalid date format for {field_name.replace('_', ' ')}"
            elif field_name in ("institution", "area"):
                self._validation_errors[field_name] = f"{field_name.replace('_', ' ').title()} is required"

        self._update_error_display()

        # Post message to notify parent of the change
        self.post_message(
            EducationChanged(
                entry_index=self.entry_index,
                field_name=field_name,
                value=value,
                is_valid=is_valid,
            )
        )


class SkillCategoryForm(Container):
    """
    Form for editing a single skill category entry.

    Provides labeled input fields for category name and keywords
    (comma-separated). Posts SkillsChanged messages when fields are modified.
    """

    DEFAULT_CSS = """
    SkillCategoryForm {
        layout: vertical;
        padding: 1;
        margin-bottom: 1;
        background: $surface;
        border: solid $primary;
    }

    SkillCategoryForm .form-row {
        layout: horizontal;
        margin-bottom: 1;
    }

    SkillCategoryForm .form-row FormField {
        width: 1fr;
        margin-right: 1;
        margin-bottom: 0;
    }

    SkillCategoryForm .form-row FormField:last-child {
        margin-right: 0;
    }

    SkillCategoryForm .error-message {
        color: $error;
        text-style: italic;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        entry: dict = None,
        entry_index: int = 0,
        **kwargs,
    ):
        """
        Initialize a SkillCategoryForm widget.

        Args:
            entry: Dictionary containing skill category data
            entry_index: Index of this entry in the skills list
            **kwargs: Additional keyword arguments for Container
        """
        super().__init__(**kwargs)
        self.entry = entry or {}
        self.entry_index = entry_index
        self._validation_errors = {}
        # Container should not take focus, only child Inputs should
        self.can_focus = False

    def compose(self) -> ComposeResult:
        """Compose the skill category form layout."""
        # First row: Category Name
        yield FormField(
            field_name="category",
            label="Category Name",
            value=self.entry.get("category", ""),
            placeholder="e.g., Programming Languages",
            id=f"skill-{self.entry_index}-category",
        )

        # Second row: Keywords (comma-separated)
        # Convert list to comma-separated string for display
        keywords_list = self.entry.get("keywords", [])
        keywords_str = ", ".join(keywords_list) if keywords_list else ""
        yield FormField(
            field_name="keywords",
            label="Keywords",
            value=keywords_str,
            placeholder="e.g., Python, Java, Go",
            id=f"skill-{self.entry_index}-keywords",
        )

        # Error message display (hidden by default)
        yield Static("", id=f"skill-{self.entry_index}-errors", classes="error-message")

    def on_mount(self) -> None:
        """Handle widget mount."""
        self._update_error_display()

    def _validate_field(self, field_name: str, value: str) -> bool:
        """
        Validate a field value.

        Args:
            field_name: Name of the field to validate
            value: Value to validate

        Returns:
            True if valid, False otherwise
        """
        from src.validators import validate_required

        # Category name is required
        if field_name == "category":
            return validate_required(value, field_name)

        # Keywords are optional
        return True

    def _update_error_display(self) -> None:
        """Update the error message display."""
        try:
            error_widget = self.query_one(f"#skill-{self.entry_index}-errors", Static)
            if self._validation_errors:
                errors = list(self._validation_errors.values())
                error_widget.update(" • ".join(errors))
                error_widget.display = True
            else:
                error_widget.display = False
        except Exception:
            # Widget may not be ready yet
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Handle input field changes.

        Args:
            event: Input changed event
        """
        # Extract field name from input ID
        input_id = event.input.id
        if not input_id or not input_id.startswith(f"skill-{self.entry_index}-"):
            return

        field_name = input_id.replace(f"skill-{self.entry_index}-", "")
        value = event.value

        # Validate the field
        is_valid = self._validate_field(field_name, value)

        # Update validation errors
        if is_valid and field_name in self._validation_errors:
            del self._validation_errors[field_name]
        elif not is_valid:
            if field_name == "category":
                self._validation_errors[field_name] = "Category name is required"

        self._update_error_display()

        # Post message to notify parent of the change
        self.post_message(
            SkillsChanged(
                entry_index=self.entry_index,
                field_name=field_name,
                value=value,
                is_valid=is_valid,
            )
        )


class ProjectEntryForm(Container):
    """
    Form for editing a single project entry.

    Provides labeled input fields for project name, description, URL,
    and highlights (comma-separated). Posts ProjectsChanged messages
    when fields are modified.
    """

    DEFAULT_CSS = """
    ProjectEntryForm {
        layout: vertical;
        padding: 1;
        margin-bottom: 1;
        background: $surface;
        border: solid $primary;
    }

    ProjectEntryForm .form-row {
        layout: horizontal;
        margin-bottom: 1;
    }

    ProjectEntryForm .form-row FormField {
        width: 1fr;
        margin-right: 1;
        margin-bottom: 0;
    }

    ProjectEntryForm .form-row FormField:last-child {
        margin-right: 0;
    }

    ProjectEntryForm .error-message {
        color: $error;
        text-style: italic;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        entry: dict = None,
        entry_index: int = 0,
        **kwargs,
    ):
        """
        Initialize a ProjectEntryForm widget.

        Args:
            entry: Dictionary containing project entry data
            entry_index: Index of this entry in the projects list
            **kwargs: Additional keyword arguments for Container
        """
        super().__init__(**kwargs)
        self.entry = entry or {}
        self.entry_index = entry_index
        self._validation_errors = {}
        # Container should not take focus, only child Inputs should
        self.can_focus = False

    def compose(self) -> ComposeResult:
        """Compose the project entry form layout."""
        # First row: Project Name (required)
        yield FormField(
            field_name="name",
            label="Project Name",
            value=self.entry.get("name", ""),
            placeholder="e.g., My Awesome Project",
            id=f"project-{self.entry_index}-name",
        )

        # Second row: Description (optional)
        yield FormField(
            field_name="description",
            label="Description",
            value=self.entry.get("description", ""),
            placeholder="e.g., A web application for...",
            id=f"project-{self.entry_index}-description",
        )

        # Third row: URL (optional)
        yield FormField(
            field_name="url",
            label="URL",
            value=self.entry.get("url", ""),
            placeholder="e.g., https://github.com/user/project",
            id=f"project-{self.entry_index}-url",
        )

        # Fourth row: Highlights (comma-separated)
        # Convert list to comma-separated string for display
        highlights_list = self.entry.get("highlights", [])
        highlights_str = ", ".join(highlights_list) if highlights_list else ""
        yield FormField(
            field_name="highlights",
            label="Highlights",
            value=highlights_str,
            placeholder="e.g., Built with Python, Used by 1000+ users",
            id=f"project-{self.entry_index}-highlights",
        )

        # Error message display (hidden by default)
        yield Static("", id=f"project-{self.entry_index}-errors", classes="error-message")

    def on_mount(self) -> None:
        """Handle widget mount."""
        self._update_error_display()

    def _validate_field(self, field_name: str, value: str) -> bool:
        """
        Validate a field value.

        Args:
            field_name: Name of the field to validate
            value: Value to validate

        Returns:
            True if valid, False otherwise
        """
        from src.validators import validate_required

        # Project name is required
        if field_name == "name":
            return validate_required(value, field_name)

        # Description, URL, and highlights are optional
        return True

    def _update_error_display(self) -> None:
        """Update the error message display."""
        try:
            error_widget = self.query_one(f"#project-{self.entry_index}-errors", Static)
            if self._validation_errors:
                errors = list(self._validation_errors.values())
                error_widget.update(" • ".join(errors))
                error_widget.display = True
            else:
                error_widget.display = False
        except Exception:
            # Widget may not be ready yet
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Handle input field changes.

        Args:
            event: Input changed event
        """
        # Extract field name from input ID
        input_id = event.input.id
        if not input_id or not input_id.startswith(f"project-{self.entry_index}-"):
            return

        field_name = input_id.replace(f"project-{self.entry_index}-", "")
        value = event.value

        # Validate the field
        is_valid = self._validate_field(field_name, value)

        # Update validation errors
        if is_valid and field_name in self._validation_errors:
            del self._validation_errors[field_name]
        elif not is_valid:
            if field_name == "name":
                self._validation_errors[field_name] = "Project name is required"

        self._update_error_display()

        # Post message to notify parent of the change
        self.post_message(
            ProjectsChanged(
                entry_index=self.entry_index,
                field_name=field_name,
                value=value,
                is_valid=is_valid,
            )
        )


class BasicsForm(Container):
    """
    Form for editing basic personal information.

    Provides labeled input fields for name, email, phone, and location.
    Posts BasicsChanged messages when fields are modified.
    """

    DEFAULT_CSS = """
    BasicsForm {
        layout: vertical;
        padding: 1;
        margin-bottom: 1;
        background: $surface;
        border: solid $secondary;
    }

    BasicsForm .form-row {
        layout: horizontal;
        margin-bottom: 1;
    }

    BasicsForm .form-row FormField {
        width: 1fr;
        margin-right: 1;
        margin-bottom: 0;
    }

    BasicsForm .form-row FormField:last-child {
        margin-right: 0;
    }
    """

    def __init__(
        self,
        basics: dict = None,
        **kwargs,
    ):
        """
        Initialize a BasicsForm widget.

        Args:
            basics: Dictionary containing basic personal info
            **kwargs: Additional keyword arguments for Container
        """
        super().__init__(**kwargs)
        self.basics = basics or {}
        # Container should not take focus, only child Inputs should
        self.can_focus = False

    def compose(self) -> ComposeResult:
        """Compose the basics form layout."""
        # First row: Name and Email
        with Horizontal(classes="form-row"):
            yield FormField(
                field_name="name",
                label="Name",
                value=self.basics.get("name", ""),
                placeholder="e.g., John Doe",
                id="basics-name",
            )
            yield FormField(
                field_name="email",
                label="Email",
                value=self.basics.get("email", ""),
                placeholder="e.g., john@example.com",
                id="basics-email",
            )

        # Second row: Phone and Location (City, Region)
        with Horizontal(classes="form-row"):
            yield FormField(
                field_name="phone",
                label="Phone",
                value=self.basics.get("phone", ""),
                placeholder="e.g., +1 234 567 8900",
                id="basics-phone",
            )
            # Location is nested: basics["location"]["city"]
            location = self.basics.get("location", {})
            yield FormField(
                field_name="city",
                label="City",
                value=location.get("city", ""),
                placeholder="e.g., San Francisco",
                id="basics-city",
            )
            yield FormField(
                field_name="region",
                label="Region",
                value=location.get("region", ""),
                placeholder="e.g., CA",
                id="basics-region",
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Handle input field changes.

        Args:
            event: Input changed event
        """
        # Extract field name from input ID
        input_id = event.input.id
        if not input_id or not input_id.startswith("basics-"):
            return

        field_name = input_id.replace("basics-", "")
        value = event.value

        # Post message to notify parent of the change
        self.post_message(
            BasicsChanged(
                field_name=field_name,
                value=value,
            )
        )


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
