# Design Spec: Web-Based Resume Editor (Minimal)

**Date:** 2026-03-23  
**Author:** AI Assistant  
**Status:** Approved

---

## 1. Overview

A minimal web-based resume editor that runs in any browser, eliminating WSL/Windows terminal compatibility issues. Built with FastAPI + HTMX + Jinja2 for server-rendered HTML with dynamic updates.

### 1.1 Goals

- Provide a browser-based form editor for resume data
- Reuse existing backend components (SessionManager, validators, engine)
- Work on any OS with a browser (Windows, WSL, Linux, macOS)
- Minimal JavaScript - HTMX for dynamic updates only

### 1.2 Non-Goals

- Live YAML preview panel
- Auto-save functionality
- Undo/redo
- Keyboard shortcuts
- Live PDF preview
- Real-time collaboration

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FastAPI Server (src/web_app.py)                            │
│  - Reuses: SessionManager, validators, engine               │
│  - Routes: /, /save, /export, /preview                      │
└─────────────────────────────────────────────────────────────┘
         │
         │ serves
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Jinja2 Templates (templates/web/)                          │
│  - base.html: Base HTML layout                              │
│  - forms.html: Resume editing forms                         │
│  - HTMX for dynamic form updates                            │
└─────────────────────────────────────────────────────────────┘
         │
         │ browser accesses
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Browser: http://localhost:8000                             │
│  - Form-based resume editor                                 │
│  - Works on Windows, WSL, any OS with browser               │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 Core Components

| Component | Technology | Responsibility |
|-----------|------------|----------------|
| **Web App** | FastAPI | HTTP routes, form handling, session management |
| **Templates** | Jinja2 + HTMX | Server-rendered HTML forms |
| **Session Manager** | Existing (src/session_manager.py) | Session persistence |
| **Validators** | Existing (src/validators.py) | Form validation |
| **Engine** | Existing (src/engine.py) | YAML export and PDF compilation |

---

## 3. User Flow

### 3.1 Primary Flow

1. **Launch:** `uv run resume-generator web`
2. **Browser opens:** Auto-opens to `http://localhost:8000`
3. **Fill forms:** Enter resume data in web forms
4. **Save:** Click "Save" button → saves to `.sessions/default.yaml`
5. **Export:** Click "Export" → writes to `inputs/private.yaml` + `inputs/public.yaml`
6. **Preview:** Click "Preview PDF" → opens compiled PDF in new tab

### 3.2 Session Commands

```bash
# Launch web editor
uv run resume-generator web

# With specific session
uv run resume-generator web --session my-resume

# Specify port
uv run resume-generator web --port 9000
```

---

## 4. Web Routes

### 4.1 FastAPI Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Main editor page with forms |
| `/save` | POST | Save session data |
| `/export` | POST | Export to inputs/ directory |
| `/preview` | GET | Open compiled PDF |
| `/health` | GET | Server status |

### 4.2 HTMX Interactions

- Form fields use `hx-post="/save"` with `hx-trigger="blur"` for auto-save on field change
- Save button uses `hx-post="/save"` with full form data
- Export button uses `hx-post="/export"` with success notification
- Preview button opens PDF in new tab

---

## 5. Form Design

### 5.1 Sections

Each section mirrors the TUI forms:

**Basics:**
- Name (required)
- Email (required, email validation)
- Phone (optional)
- City (optional)
- Region (optional)

**Work Experience:**
- Company (required)
- Position (required)
- Location (optional)
- Start Date (YYYY-MM)
- End Date (YYYY-MM or Present)
- Summary (textarea, bullet points)

**Education:**
- Institution (required)
- Area of Study (required)
- Location (optional)
- Start Date (YYYY-MM)
- End Date (YYYY-MM)
- Score/GPA (optional)

**Skills:**
- Category Name (required)
- Keywords (comma-separated)

**Projects:**
- Project Name (required)
- Description (optional)
- URL (optional)
- Highlights (comma-separated)

### 5.2 Validation

- **Client-side:** HTML5 validation (required, email, pattern)
- **Server-side:** Reuses `src/validators.py` functions
- **Error display:** Inline error messages below fields

---

## 6. Session Management

### 6.1 Storage

- **Directory:** `.sessions/` (same as TUI)
- **File format:** YAML
- **Session name:** From `--session` flag or "default"

### 6.2 Save Behavior

- **Manual save:** Click "Save" button
- **Auto-save on blur:** Optional, field-level save when user moves to next field
- **Export:** Writes to `inputs/private.yaml` and `inputs/public.yaml`

---

## 7. Error Handling

| Scenario | Behavior |
|----------|----------|
| Validation error | Inline error message, form not saved |
| Save failure | Error notification, retry option |
| Export failure | Error notification with details |
| PDF compile error | Show error message, link to error log |
| Server unavailable | Browser shows standard connection error |

---

## 8. Testing Strategy

### 8.1 Unit Tests

- `test_web_app.py`: Route tests, form handling
- `test_session_integration.py`: Session save/load via web

### 8.2 Integration Tests

- Form submission → session save → export flow
- Validation error handling

### 8.3 Manual Testing

- Open in browser, fill forms, verify save/export
- Test on Windows browser accessing WSL server

---

## 9. Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `src/web_app.py` | FastAPI web application |
| `templates/web/base.html` | Base HTML template |
| `templates/web/forms.html` | Resume editing forms |
| `tests/test_web_app.py` | Web app tests |

### Modified Files

| File | Changes |
|------|---------|
| `src/main.py` | Add `web` command |
| `requirements.txt` | HTMX already included (no new deps) |

---

## 10. Dependencies

### Existing (reused)

```
fastapi>=0.109.0   # Already installed
uvicorn>=0.27.0    # Already installed
jinja2             # Already installed
pyyaml             # Already installed
```

### No new dependencies

HTMX loaded from CDN (no install needed).

---

## 11. Implementation Phases

### Phase 1: Web App Skeleton
- FastAPI app with `/` route
- Basic HTML template
- Launch command in main.py

### Phase 2: Forms Implementation
- All form sections (Basics, Work, Education, Skills, Projects)
- Form data binding to SessionManager

### Phase 3: Save/Export
- Save endpoint
- Export endpoint
- Success/error notifications

### Phase 4: Validation
- Client-side HTML5 validation
- Server-side validation with validators module
- Inline error display

### Phase 5: Testing & Polish
- Unit tests
- Manual testing on Windows browser
- Documentation

---

## 12. Success Criteria

- [ ] Browser opens to form editor at `http://localhost:8000`
- [ ] All form sections visible and editable
- [ ] Save button stores data to `.sessions/default.yaml`
- [ ] Export button writes to `inputs/` directory
- [ ] Validation errors shown inline
- [ ] Works from Windows browser accessing WSL server
- [ ] All existing 98 tests still pass
- [ ] New web app tests pass

---

## 13. Open Questions (Resolved)

1. **HTMX from CDN or vendored?** → CDN for simplicity
2. **Auto-save on blur or manual only?** → Manual save button only (minimal scope)
3. **PDF preview in same tab or new?** → New tab to avoid losing form state
