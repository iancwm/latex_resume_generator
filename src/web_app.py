"""
Web-Based Resume Editor for LaTeX Resume Generator.

Provides a browser-based form editor for resume data using FastAPI + HTMX + Jinja2.
Reuses existing backend components (SessionManager, validators, engine).
"""

import os
import yaml
import webbrowser
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from src.session_manager import SessionManager
from src.validators import validate_email, validate_date, validate_required
from src.engine import generate as engine_generate


app = FastAPI(title="Resume Editor")

# Template directory
BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates" / "web"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.cache_size = 0  # Disable template cache for development
templates.env.autoescape = True  # Enable autoescaping

# Session manager instance
session_manager = SessionManager()

# Current session name (can be overridden per-request via query param)
DEFAULT_SESSION = "default"


def get_session_name(session: Optional[str] = None) -> str:
    """Get session name from parameter or default."""
    return session if session else DEFAULT_SESSION


def load_session_data(session_name: str) -> dict:
    """Load session data or return empty structure."""
    data = session_manager.load(session_name)
    if data is None:
        data = {
            "basics": {"location": {}},
            "work": [{}],
            "education": [{}],
            "skills": [{}],
            "projects": [{}]
        }
    return data


def validate_form_data(data: dict) -> list[dict]:
    """
    Validate form data and return list of errors.
    
    Args:
        data: Form data dict
        
    Returns:
        List of error dicts with field and message keys
    """
    errors = []
    
    # Validate basics
    basics = data.get("basics", {})
    if not basics.get("name", "").strip():
        errors.append({"field": "basics.name", "message": "Name is required"})
    if not basics.get("email", "").strip():
        errors.append({"field": "basics.email", "message": "Email is required"})
    elif not validate_email(basics.get("email", "")):
        errors.append({"field": "basics.email", "message": "Invalid email format"})
    
    # Validate work entries
    for i, work in enumerate(data.get("work", [])):
        if work.get("company", "").strip() and not work.get("company", "").strip():
            errors.append({"field": f"work.{i}.company", "message": "Company is required"})
        if work.get("position", "").strip() and not work.get("position", "").strip():
            errors.append({"field": f"work.{i}.position", "message": "Position is required"})
        start_date = work.get("start_date", "")
        if start_date and not validate_date(start_date):
            errors.append({"field": f"work.{i}.start_date", "message": "Invalid date format (YYYY-MM)"})
        end_date = work.get("end_date", "")
        if end_date and end_date != "Present" and not validate_date(end_date):
            errors.append({"field": f"work.{i}.end_date", "message": "Invalid date format (YYYY-MM)"})
    
    # Validate education entries
    for i, edu in enumerate(data.get("education", [])):
        if edu.get("institution", "").strip() and not edu.get("institution", "").strip():
            errors.append({"field": f"education.{i}.institution", "message": "Institution is required"})
        if edu.get("area", "").strip() and not edu.get("area", "").strip():
            errors.append({"field": f"education.{i}.area", "message": "Area of study is required"})
    
    return errors


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    session: Optional[str] = None,
    message: Optional[str] = None,
    message_type: Optional[str] = None
):
    """Main editor page with resume forms."""
    session_name = get_session_name(session)
    data = load_session_data(session_name)

    return templates.TemplateResponse(
        request=request,
        name="forms.html",
        context={
            "data": data,
            "session_name": session_name,
            "message": message,
            "message_type": message_type,
        },
    )


@app.post("/save")
async def save_session(
    request: Request,
    session: Optional[str] = None,
    name: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    city: str = Form(""),
    region: str = Form(""),
    work_entries: str = Form("[]"),
    education_entries: str = Form("[]"),
    skills_entries: str = Form("[]"),
    projects_entries: str = Form("[]"),
):
    """Save session data."""
    try:
        session_name = get_session_name(session)
        
        # Build data structure from form fields
        import json
        
        data = {
            "basics": {
                "name": name.strip() if name.strip() else "",
                "email": email.strip() if email.strip() else "",
                "phone": phone.strip() if phone.strip() else "",
                "location": {}
            }
        }
        
        if city.strip():
            data["basics"]["location"]["city"] = city.strip()
        if region.strip():
            data["basics"]["location"]["region"] = region.strip()
        
        # Parse JSON-encoded entries
        try:
            data["work"] = json.loads(work_entries) if work_entries else [{}]
            data["education"] = json.loads(education_entries) if education_entries else [{}]
            data["skills"] = json.loads(skills_entries) if skills_entries else [{}]
            data["projects"] = json.loads(projects_entries) if projects_entries else [{}]
        except json.JSONDecodeError:
            return HTMLResponse(
                '<div id="save-notification" class="notification error">Error: Invalid form data</div>',
                headers={"HX-Swap-Outer-True": "#save-notification"}
            )
        
        # Validate
        errors = validate_form_data(data)
        if errors:
            error_messages = "; ".join([e["message"] for e in errors])
            return HTMLResponse(
                f'<div id="save-notification" class="notification error">Validation error: {error_messages}</div>',
                headers={"HX-Swap-Outer-True": "#save-notification"}
            )
        
        # Save session
        session_manager.save(session_name, data)
        
        return HTMLResponse(
            f'<div id="save-notification" class="notification success">Session "{session_name}" saved successfully!</div>',
            headers={"HX-Swap-Outer-True": "#save-notification"}
        )
        
    except Exception as e:
        return HTMLResponse(
            f'<div id="save-notification" class="notification error">Save failed: {str(e)}</div>',
            headers={"HX-Swap-Outer-True": "#save-notification"}
        )


@app.post("/export")
async def export_session(
    request: Request,
    session: Optional[str] = None,
):
    """Export session to inputs/private.yaml and inputs/public.yaml."""
    try:
        session_name = get_session_name(session)
        data = load_session_data(session_name)

        # Check if there's meaningful data to export (name and email at minimum)
        basics = data.get("basics", {})
        if not basics or (not basics.get("name") and not basics.get("email")):
            return HTMLResponse(
                '<div id="export-notification" class="notification error">No data to export. Please save first.</div>',
                headers={"HX-Swap-Outer-True": "#export-notification"}
            )

        # Split into private (basics) and public (everything else)
        private_data = {"basics": basics}
        public_data = {k: v for k, v in data.items() if k != "basics"}

        # Ensure inputs directory exists
        inputs_dir = BASE_DIR / "inputs"
        inputs_dir.mkdir(exist_ok=True)

        # Write files
        with open(inputs_dir / "private.yaml", "w") as f:
            yaml.dump(private_data, f, default_flow_style=False, sort_keys=False)

        with open(inputs_dir / "public.yaml", "w") as f:
            yaml.dump(public_data, f, default_flow_style=False, sort_keys=False)

        return HTMLResponse(
            '<div id="export-notification" class="notification success">Exported to inputs/private.yaml and inputs/public.yaml!</div>',
            headers={"HX-Swap-Outer-True": "#export-notification"}
        )

    except Exception as e:
        return HTMLResponse(
            f'<div id="export-notification" class="notification error">Export failed: {str(e)}</div>',
            headers={"HX-Swap-Outer-True": "#export-notification"}
        )


@app.get("/preview")
async def preview_pdf(session: Optional[str] = None):
    """Generate and open PDF preview."""
    try:
        session_name = get_session_name(session)
        data = load_session_data(session_name)
        
        if not data:
            raise HTTPException(status_code=400, detail="No session data to preview")
        
        # Split into private/public
        private_data = {"basics": data.get("basics", {})}
        public_data = {k: v for k, v in data.items() if k != "basics"}
        
        # Generate to temp files
        temp_dir = BASE_DIR / "dist"
        temp_dir.mkdir(exist_ok=True)
        
        private_file = temp_dir / "web_private.yaml"
        public_file = temp_dir / "web_public.yaml"
        output_tex = temp_dir / "web_resume.tex"
        output_pdf = temp_dir / "web_resume.pdf"
        
        with open(private_file, "w") as f:
            yaml.dump(private_data, f, default_flow_style=False, sort_keys=False)
        
        with open(public_file, "w") as f:
            yaml.dump(public_data, f, default_flow_style=False, sort_keys=False)
        
        # Get template path
        from src.config import load_config
        config = load_config()
        template_name = config.get("defaults", {}).get("resume_template", "modern")
        template_path = None
        for tmpl in config.get("templates", []):
            if tmpl.get("name") == template_name and "resume" in tmpl.get("file_path", ""):
                template_path = tmpl.get("file_path")
                break
        
        if not template_path:
            template_path = "templates/resume/modern.tex"
        
        # Generate resume
        engine_generate(
            str(private_file),
            str(public_file),
            template_path,
            str(output_tex),
            redacted=False,
            compile=True
        )
        
        # Open in browser
        webbrowser.open(f"file://{output_pdf.absolute()}")
        
        return RedirectResponse(url="/?session={session_name}&message=PDF+generated+successfully&message_type=success")
        
    except Exception as e:
        return RedirectResponse(url=f"/?session={session_name}&message=Preview+failed:+{str(e)}&message_type=error")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "resume-editor"}


def run_web_server(session_name: str = "default", port: int = 8000, open_browser: bool = True):
    """
    Run the web editor server.

    Args:
        session_name: Session name to use
        port: Port to run on
        open_browser: Whether to open browser automatically
    """
    global DEFAULT_SESSION
    DEFAULT_SESSION = session_name
    
    if open_browser:
        # Open browser after a short delay to let server start
        import threading
        def open_later():
            import time
            time.sleep(1.5)
            webbrowser.open(url)
        threading.Thread(target=open_later, daemon=True).start()
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    run_web_server()
