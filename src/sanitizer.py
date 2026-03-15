import re

def escape_latex(text: str) -> str:
    """
    Escapes LaTeX special characters.
    """
    if not isinstance(text, str):
        return text

    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    
    # Use a regex to replace all at once to avoid double escaping
    pattern = re.compile('|'.join(re.escape(key) for key in replacements.keys()))
    return pattern.sub(lambda m: replacements[m.group(0)], text)

def smart_quotes(text: str) -> str:
    """
    Replaces "text" with ``text''.
    """
    if not isinstance(text, str):
        return text

    # Simple logic: replace opening " with `` and closing " with ''
    # This assumes balanced quotes.
    # A slightly more robust regex approach:
    # Replace " at start of string or after space with ``
    # Replace " at end of string or after non-space with ''
    
    # Step 1: Replace opening quotes (start of line or following space/punctuation)
    text = re.sub(r'(^|[\s\(\[\{])"', r'\1``', text)
    
    # Step 2: Replace closing quotes (anything else)
    text = re.sub(r'"', r"''", text)
    
    return text

def sanitize(value):
    """
    Applies all sanitization to a value (string or list of strings).
    """
    if isinstance(value, str):
        return smart_quotes(escape_latex(value))
    elif isinstance(value, list):
        return [sanitize(v) for v in value]
    elif isinstance(value, dict):
        return {k: sanitize(v) for k, v in value.items()}
    return value
