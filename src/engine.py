import yaml
import jinja2
import os
import subprocess
from sanitizer import escape_latex, smart_quotes

def compile_pdf(tex_path: str, output_dir: str) -> bool:
    """
    Compiles a .tex file to PDF using xelatex.
    Runs twice for proper reference handling.
    """
    cmd = ['xelatex', f'-output-directory={output_dir}', tex_path]
    try:
        # First pass
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        # Second pass
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error compiling PDF: {e.stderr}")
        raise RuntimeError(f"LaTeX compilation failed: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("xelatex not found. Please ensure it is installed and in your PATH.")

def load_yaml(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}

def redact_data(data, is_redaction_mode=True, default_private=True):
    """
    Recursively processes data for privacy overrides and redaction.
    - is_redaction_mode: Whether to actually redact (True) or just unwrap (False).
    - default_private: Default behavior for strings if no override is present.
    """
    if isinstance(data, dict):
        return {k: redact_inner(k, v, is_redaction_mode, default_private) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_data(item, is_redaction_mode, default_private) for item in data]
    elif isinstance(data, str):
        if is_redaction_mode and default_private:
            return "REDACTED: VALUE"
        return data
    return data

def redact_inner(key, value, is_redaction_mode, default_private):
    """ Helper to handle redaction with key context for better placeholders. """
    if isinstance(value, dict):
        # Check for override structure: {"value": "...", "private": bool}
        if "value" in value and "private" in value and len(value) == 2:
            should_redact = value["private"] if is_redaction_mode else False
            if should_redact:
                return "REDACTED: {}".format(key.upper())
            else:
                # Override says it's NOT private, so pass default_private=False
                return redact_data(value["value"], is_redaction_mode, default_private=False)
        return redact_data(value, is_redaction_mode, default_private)
    elif isinstance(value, list):
        return [redact_data(item, is_redaction_mode, default_private) for item in value]
    elif isinstance(value, str):
        if is_redaction_mode and default_private:
            return "REDACTED: {}".format(key.upper())
        return value
    return value

def sanitize_data(data):
    """
    Recursively applies LaTeX escaping and smart quotes.
    Converts None to empty string to prevent Jinja2 filter errors.
    """
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(v) for v in data]
    elif isinstance(data, str):
        escaped = escape_latex(data)
        return smart_quotes(escaped)
    elif data is None:
        return ""
    else:
        return data

def render_template(template_path: str, output_path: str, context: dict):
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)
    
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        block_start_string=r'\BLOCK{',
        block_end_string='}',
        variable_start_string=r'\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
    )
    
    template = env.get_template(template_file)
    rendered = template.render(**context)
    
    with open(output_path, 'w') as f:
        f.write(rendered)

def generate(private_path, public_path, template_path, output_path, redacted=False, compile=False):
    private_data = load_yaml(private_path)
    public_data = load_yaml(public_path)
    
    # Apply privacy logic to both, but with different defaults
    private_data = redact_data(private_data, is_redaction_mode=redacted, default_private=True)
    public_data = redact_data(public_data, is_redaction_mode=redacted, default_private=False)
        
    full_data = {**public_data, **private_data}
    
    clean_data = sanitize_data(full_data)
    
    render_template(template_path, output_path, clean_data)
    
    if compile:
        output_dir = os.path.dirname(output_path) or "."
        compile_pdf(output_path, output_dir)
