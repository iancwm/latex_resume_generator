# Design Spec: TUI Editor with Live Web Preview

**Date:** 2026-03-23  
**Author:** AI Assistant  
**Status:** In Review (Issues Addressed)

---

## 1. Overview

A comprehensive, IDE-like terminal user interface (TUI) for editing resume data, paired with a live web-based PDF preview. This replaces the existing `generate_interactive` command with a modern, feature-rich experience built on the Textual framework and FastAPI.

### 1.1 Goals

- Provide a full-screen, split-pane TUI for resume data entry
- Enable live PDF preview in a browser tab via a background FastAPI server
- Implement robust session management with auto-save and crash recovery
- Maintain the CLI-first, developer-friendly experience of the existing tool

### 1.2 Non-Goals

- Web-based resume editor (this is a TUI, not a web app)
- Real-time collaboration features
- Support for multiple simultaneous TUI sessions (single-user focus)

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  resume-generator (Typer CLI)                                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  generate-edit (Textual TUI App)                           │ │
│  │  ┌─────────────────┬─────────────────────────────────────┐ │ │
│  │  │  Form Editor    │  YAML Preview Panel                 │ │ │
│  │  │  (Left Pane)    │  (Right Pane)                       │ │ │
│  │  │                 │                                     │ │ │
│  │  │  • Basics       │  • Syntax-highlighted YAML          │ │ │
│  │  │  • Work         │  • Live updates as you type         │ │ │
│  │  │  • Education    │  • Pygments highlighting            │ │ │
│  │  │  • Skills       │                                     │ │ │
│  │  │  • Projects     │                                     │ │ │
│  │  │  • Validation   │                                     │ │ │
│  │  └─────────────────┴─────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │  Status Bar: [Auto-save: ON] [Preview: Running :8000]      │ │
│  │  Keys: ^S Save | ^Q Quit | ^P Toggle Preview | ^Z Undo     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  preview-server (FastAPI + Uvicorn)                        │ │
│  │  - Spawns on TUI launch (port 8000)                        │ │
│  │  - Watches session YAML for changes                        │ │
│  │  - Compiles LaTeX → PDF on save                            │ │
│  │  - Serves PDF to browser                                   │ │
│  │  - Persists across TUI sessions                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Auto-opens
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Browser: http://localhost:8000/preview                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Live PDF Preview                                         │  │
│  │  - Auto-refreshes on compile complete                      │  │
│  │  - Shows actual rendered LaTeX output                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 Core Components

| Component | Technology | Responsibility |
|-----------|------------|----------------|
| **TUI App** | Textual | Form-based editor, navigation, validation, YAML preview |
| **Session Manager** | Python + YAML | Auto-save, crash recovery, named sessions |
| **Preview Server** | FastAPI + Uvicorn | HTTP server, LaTeX compilation, PDF serving |
| **State Bridge** | HTTP POST + Atomic YAML writes | TUI POSTs payload → Server writes atomically → Compiles |

### 2.2 State Synchronization

**Problem:** Concurrent writes (auto-save + manual save) and mid-write reads can cause corruption.

**Solution:**

1. **Atomic Writes:** All YAML writes use write-to-temp-then-rename pattern:
   ```python
   # Write to temp file, then atomic rename
   temp_path = f"{target_path}.tmp.{os.getpid()}"
   with open(temp_path, 'w') as f:
       yaml.dump(data, f)
   os.replace(temp_path, target_path)  # Atomic on POSIX
   ```

2. **File Locking:** Server acquires shared lock for reads, TUI acquires exclusive lock for writes:
   ```python
   import fcntl
   with open(path, 'r+') as f:
       fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock for read
       # or fcntl.LOCK_EX for write
   ```

3. **Compile Trigger via HTTP:** TUI sends POST `/compile` with session payload, server writes and compiles. No file polling race conditions.

4. **Server Identity:** Server writes PID file (`.sessions/preview_server.pid`) and includes server_id in `/health` response. TUI verifies it's reconnecting to its own server instance.

---

## 3. User Flow

### 3.1 Primary Flow

1. **Launch:** `resume-generator edit [--session <name>]`
2. **TUI opens:** Full-screen editor with split panes
3. **Preview server starts:** Auto-opens browser tab at `localhost:8000/preview`
4. **Edit:** Navigate sections, fill forms, see YAML update live
5. **Auto-save:** Every 30 seconds to `.sessions/<session_name>.yaml`
6. **Save & Compile:** Press `Ctrl+S` → writes to `inputs/` → triggers server compile
7. **Browser updates:** PDF refreshes automatically
8. **Exit:** `Ctrl+Q` — server keeps running, session persists
9. **Resume:** `resume-generator edit --resume` or `--session <name>`

### 3.2 Session Commands

```bash
# List all sessions
resume-generator sessions

# Resume most recent session
resume-generator edit --resume

# Resume specific session
resume-generator edit --session alex_v2

# Delete a session
resume-generator sessions --delete alex_v2

# Start fresh session with name
resume-generator edit --session new_project
```

---

## 4. TUI Design

### 4.1 Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  Resume Editor - Session: alex_v2                    [_][□][X]  │
├─────────────────────────────┬────────────────────────────────────┤
│  Form Editor                │  YAML Preview                      │
│  ┌─────────────────────────┐ │  ┌──────────────────────────────┐ │
│  │ [Basics] [Work] [Edu]   │ │  │ basics:                       │ │
│  │ [Skills] [Projects]     │ │  │   name: "Alexander Sterling"  │ │
│  │                         │ │  │   email: "alex@example.com"   │ │
│  │ Company: _____________  │ │  │ work:                         │ │
│  │ Position: ____________  │ │  │   - company: "Goldman Sachs"  │ │
│  │ Location: ____________  │ │  │     position: "Analyst"       │ │
│  │ Start: ____-__  End: __ │ │  │     summary:                  │ │
│  │                         │ │  │       - "Executed DCF..."     │ │
│  │ Summary Points:         │ │  │                               │ │
│  │ ┌─────────────────────┐ │ │  │                               │ │
│  │ │ • Executed DCF...   │ │ │  │                               │ │
│  │ │ • Collaborated on.. │ │ │  │                               │ │
│  │ │ [+ Add Point]       │ │ │  │                               │ │
│  │ └─────────────────────┘ │ │  │                               │ │
│  │                         │ │  │                               │ │
│  │ [Save] [Cancel]         │ │  │                               │ │
│  └─────────────────────────┘ │  └──────────────────────────────┘ │
├─────────────────────────────┴────────────────────────────────────┤
│  ^S Save  ^Q Quit  ^P Preview  ^Z Undo  |  Auto-save: ON  │ ✓   │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+S` | Save and compile |
| `Ctrl+Q` | Quit (with confirmation if unsaved) |
| `Ctrl+P` | Toggle preview server |
| `Ctrl+Z` | Undo last edit |
| `Ctrl+Y` | Redo |
| `Tab` | Next field |
| `Shift+Tab` | Previous field |
| `Ctrl+1..5` | Jump to section (1=Basics, 2=Work, etc.) |
| `F1` | Help / Key reference |

### 4.3 Sections

Each section has a dedicated form:

- **Basics:** Name, Label, Email, Phone, URL, Location (nested), Profiles (list)
- **Work:** Company, Position, Location, Start/End Dates, Summary (list with validation)
- **Education:** Institution, Area, Location, Start/End Dates, Score, Honors, Courses
- **Skills:** Category Name, Keywords (multi-select)
- **Projects:** Name, Description, URL, Highlights (list)

---

## 5. Session Management

### 5.1 Storage

- **Directory:** `.sessions/`
- **File format:** YAML (merged private + public structure)
- **Naming:** `<session_name>.yaml` or `session_<timestamp>.yaml` for auto-named
- **Permissions:** `0600` (owner read/write only) - enforced on file creation
- **Security Warning:** Users should not symlink `.sessions/` to cloud-synced directories (Dropbox, iCloud, etc.) as session files contain PII

### 5.2 Auto-Save

- **Interval:** Every 30 seconds
- **Trigger:** On explicit save (`Ctrl+S`)
- **Location:** `.sessions/<session_name>.yaml`
- **Method:** Atomic write (temp file + rename)

### 5.3 Crash Recovery

- On TUI launch, detect incomplete sessions (modified within last 24 hours)
- Prompt: "Recover unsaved session 'alex_v2' from 2 hours ago? [Y/n]"
- Restore from `.sessions/<session_name>.yaml`

### 5.4 Undo/Redo Design

**Implementation:** Command pattern with in-memory state stack.

- **Scope:** Per-field edits (each keystroke batch is a single undoable command)
- **Stack Depth:** 50 states maximum (FIFO eviction)
- **Memory:** Each state is a deep copy of the session data dict (~10-50KB per state, max ~2.5MB total)
- **Lifetime:** Session-scoped (undo history does NOT persist across TUI restarts)
- **Shortcuts:** `Ctrl+Z` (undo), `Ctrl+Y` (redo)
- **Edge Cases:**
  - Undo across auto-save boundaries: Auto-save does NOT clear undo stack
  - Undo after explicit save (`Ctrl+S`): Clears undo stack (save is a commit point)

### 5.5 Session Lifecycle

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Create    │────▶│    Edit     │────▶│    Save     │
└─────────────┘     └─────────────┘     └─────────────┘
                          │                   │
                          │ Auto-save         │ Write to inputs/
                          ▼                   ▼
                    .sessions/           inputs/private.yaml
                                         inputs/public.yaml
```

---

## 6. Preview Server

### 6.1 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Redirect to `/preview` |
| `/preview` | GET | HTML page with embedded PDF viewer + SSE listener |
| `/preview.pdf` | GET | Raw PDF file |
| `/compile` | POST | Trigger manual compilation |
| `/health` | GET | Server status, last compile time, server_id |
| `/error` | GET | Last compilation error (if any) |
| `/events` | GET | Server-Sent Events stream for auto-refresh notifications |

### 6.2 Compilation Flow

```
1. User presses Ctrl+S in TUI
2. TUI POST /compile with session payload
3. Server writes atomically to inputs/private.yaml + inputs/public.yaml
4. Server calls engine_generate() with compile=True
5. On success: PDF written to dist/resume.pdf
6. Server sends SSE event: { event: "compile_complete", timestamp: "..." }
7. Browser receives SSE, reloads PDF iframe
8. On error: Server sends SSE event: { event: "compile_error", message: "..." }
   Browser shows error overlay, retains last successful PDF
```

**Server-Sent Events (SSE):**
- Browser opens persistent connection to `/events`
- Server pushes compile status updates
- Auto-reconnect on connection loss
- Simpler than WebSocket, more efficient than polling

### 6.3 Server Persistence

- **Start:** Auto-spawned on TUI launch (checks for existing server first)
- **Run:** Continues running after TUI exits
- **Stop:** `resume-generator preview --stop` or process kill
- **Port:** 8000 (configurable via env `PREVIEW_PORT`)
- **PID File:** `.sessions/preview_server.pid` - used for server identity verification
- **Stale Server Cleanup:** If no TUI connection in 24 hours, server auto-shuts down
- **Ephemeral Mode:** `resume-generator edit --no-persist` - server shuts down when TUI exits
- **Server Identity:** `/health` returns `{ server_id: "uuid", pid: 12345, started_at: "..." }`
  TUI verifies server_id matches its spawned instance before reconnecting

---

## 7. Error Handling

| Scenario | TUI Behavior | Server Behavior |
|----------|--------------|-----------------|
| LaTeX compile fails | Status bar: "Compile failed" (red) | Return error JSON, serve error page, send SSE error event |
| Server port in use | Detect via `/health`, verify server_id, reconnect or error | Continue running |
| Session file corrupted | Show recovery options dialog | N/A |
| Browser tab closed | N/A | Server keeps running, SSE connection closed |
| Invalid YAML | Inline validation error (prevents save) | N/A |
| Missing LaTeX | Detected on TUI startup, show install instructions, disable preview features | Return "LaTeX not found" error on compile attempt |
| Server crashes mid-compile | TUI shows "Server unavailable, retrying..." | N/A (restart required) |
| Port conflict with non-preview process | Error: "Port 8000 in use by another process" with instructions to free port or use `PREVIEW_PORT` env | N/A |

### 7.1 LaTeX Detection

- **Timing:** On TUI startup (before editor loads)
- **Method:** Check for `xelatex` in PATH via `shutil.which("xelatex")`
- **Graceful Degradation:** If LaTeX not found:
  - TUI remains fully functional for YAML editing
  - Preview panel shows: "LaTeX not installed - PDF preview unavailable"
  - Install instructions shown based on platform:
    - Linux: `apt install texlive-xetex` or `dnf install texlive-xetex`
    - macOS: `brew install --cask mactex-no-gui`
    - General: https://www.latex-project.org/get/

---

## 8. Testing Strategy

### 8.1 Unit Tests

| Module | Test Cases |
|--------|------------|
| `test_session_manager.py` | Save/load roundtrip, atomic write verification, crash recovery, merge logic, file permissions |
| `test_validation.py` | Date formats (YYYY-MM, Present), required field validation, bullet point consistency checks |
| `test_preview_server.py` | Compile trigger handling, SSE event emission, error response format, server identity verification |
| `test_atomic_writes.py` | Concurrent write safety, temp file cleanup, rename atomicity |

### 8.2 Integration Tests

| Scenario | Expected Behavior |
|----------|-------------------|
| TUI → Session file → Server → PDF | Full flow completes, PDF updated |
| Multi-session isolation | Session A edits don't affect Session B |
| Auto-save timing | Auto-save occurs at 30s intervals, doesn't interfere with manual save |
| Server crash during compile | TUI shows error, next save retries successfully |
| Undo/redo across saves | Undo stack clears after Ctrl+S, works correctly before |

### 8.3 E2E Tests

- Scripted TUI interaction using Textual's `run_test()` harness
- Verify PDF output content matches entered data
- Test recovery flow: start TUI, kill -9, restart, verify recovery prompt

### 8.4 Coverage Requirements

- **Minimum:** 80% line coverage for new modules
- **Critical paths:** 100% coverage for session manager, atomic writes, validation

---

## 9. Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/tui_app.py` | Create | Textual TUI application |
| `src/preview_server.py` | Create | FastAPI preview server |
| `src/session_manager.py` | Create | Session persistence & recovery |
| `src/main.py` | Modify | Add `edit`, `sessions`, `preview` commands |
| `tests/test_tui_app.py` | Create | TUI component tests |
| `tests/test_session_manager.py` | Create | Session manager tests |
| `tests/test_preview_server.py` | Create | Server tests |
| `.sessions/` | Create | Session storage directory |
| `.gitignore` | Modify | Add `.sessions/*.yaml` |
| `requirements.txt` | Modify | Add `textual`, `fastapi`, `uvicorn`, `websockets` |

---

## 10. Dependencies

### 10.1 New Dependencies

```
textual>=0.50.0      # TUI framework
fastapi>=0.109.0     # Preview server
uvicorn>=0.27.0      # ASGI server
websockets>=12.0     # Live reload (optional)
pygments>=2.17.0     # Syntax highlighting (Textual dependency)
```

### 10.2 Existing Dependencies (retained)

```
typer                # CLI framework
pyyaml               # YAML parsing
jinja2               # Template rendering
simple-term-menu     # (optional, can be removed later)
```

---

## 11. Phase Breakdown

### Phase 0: Spike (Risk Reduction)
- Validate Textual + FastAPI integration works as expected
- Test atomic write patterns and SSE browser compatibility
- **Checkpoint:** Working prototype of TUI with basic form + server health check

### Phase 1: Foundation
- Textual TUI skeleton with split panes
- Basic form editor for one section (Work)
- Session manager with auto-save (atomic writes)
- **Checkpoint:** Can edit work entries, auto-saves to `.sessions/`

### Phase 2: Full Editor
- All sections (Basics, Work, Education, Skills, Projects)
- Validation logic (dates, required fields, bullet consistency)
- YAML preview panel with Pygments highlighting
- Undo/redo implementation
- **Checkpoint:** Full resume editable in TUI with undo support

### Phase 3: Preview Server (uses default session)
- FastAPI server with LaTeX compilation
- Browser auto-open on server start
- SSE-based auto-refresh
- Compile-on-save integration (POST /compile)
- Error handling and display
- **Checkpoint:** Save in TUI → PDF updates in browser (using `default.yaml` session)

### Phase 4: Session Management
- Named sessions (`--session <name>` flag)
- Session list/delete commands
- Crash recovery flow
- Server identity verification (PID file, server_id)
- **Checkpoint:** Can resume interrupted sessions, multiple named sessions

### Phase 5: Polish & Testing
- All keyboard shortcuts
- Full test suite (unit, integration, E2E)
- Documentation
- **Checkpoint:** Production-ready feature, all tests passing

---

## 12. Resolved Design Decisions

The following questions were resolved during spec review:

1. **LaTeX preview fallback:** ✅ RESOLVED - TUI shows "LaTeX not installed" placeholder in preview panel. YAML editing remains functional. Install instructions shown based on platform.

2. **Multi-template support:** ✅ DEFERRED - Out of scope for initial implementation. Template selection remains a CLI flag feature (`--template-name`). Can be added to TUI in a future enhancement.

3. **Cover letter editing:** ✅ DEFERRED - Separate command (`resume-generator edit-cover-letter`). Shares same TUI framework but different form fields and template. Future enhancement may unify both editors.

---

## 13. Success Criteria

- [ ] User can edit all resume sections in a split-pane TUI
- [ ] YAML preview updates live as user types
- [ ] Auto-save every 30 seconds to session file
- [ ] Preview server auto-starts and opens browser tab
- [ ] Save in TUI triggers PDF compilation
- [ ] Browser shows updated PDF within 5 seconds of save
- [ ] Session recovery works after simulated crash
- [ ] All 29 existing tests still pass
- [ ] New TUI/server tests cover core functionality
