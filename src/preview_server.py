import os
import uuid
import time
import threading
import asyncio
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, StreamingResponse, FileResponse
import uvicorn

from src.session_manager import atomic_write
from src.engine import generate


def create_app(sessions_dir: str, inputs_dir: str, dist_dir: str) -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(title="Resume Preview Server")

    server_id = str(uuid.uuid4())
    started_at = time.time()
    last_error: Optional[str] = None

    @app.get("/health")
    async def health():
        return {
            "server_id": server_id,
            "pid": os.getpid(),
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(started_at)),
        }

    @app.get("/")
    async def root():
        return RedirectResponse(url="/preview")

    @app.post("/compile")
    async def compile(payload: dict):
        """
        Compile resume from private and public YAML data.
        
        Expects: {"private": {...}, "public": {...}}
        Returns: {"success": true} or {"error": "message"}
        """
        nonlocal last_error
        try:
            # Validate payload
            if "private" not in payload or "public" not in payload:
                last_error = "Missing 'private' or 'public' in payload"
                return JSONResponse(
                    status_code=400,
                    content={"error": last_error}
                )

            private_data = payload["private"]
            public_data = payload["public"]

            # Create temp directory for this compile session
            compile_tmp_dir = Path(tempfile.mkdtemp(dir=sessions_dir))

            try:
                # Write private and public YAML files atomically
                private_path = compile_tmp_dir / "private.yaml"
                public_path = compile_tmp_dir / "public.yaml"
                output_tex_path = compile_tmp_dir / "resume.tex"

                import yaml
                atomic_write(
                    str(private_path),
                    yaml.dump(private_data, default_flow_style=False)
                )
                atomic_write(
                    str(public_path),
                    yaml.dump(public_data, default_flow_style=False)
                )

                # Get template path (use default template)
                template_path = Path(inputs_dir).parent / "templates" / "resume.tex"
                if not template_path.exists():
                    # Fallback to common template locations
                    template_path = Path("templates/resume.tex")

                # Generate and compile
                generate(
                    private_path=str(private_path),
                    public_path=str(public_path),
                    template_path=str(template_path),
                    output_path=str(output_tex_path),
                    redacted=False,
                    compile=True
                )

                last_error = None
                return {"success": True, "output_dir": str(compile_tmp_dir)}

            except Exception as e:
                last_error = str(e)
                return JSONResponse(
                    status_code=500,
                    content={"error": last_error}
                )

        except Exception as e:
            last_error = str(e)
            return JSONResponse(
                status_code=500,
                content={"error": last_error}
            )

    @app.get("/error")
    async def error():
        """Return the last error message."""
        return {"last_error": last_error}

    @app.get("/events")
    async def events():
        """SSE endpoint for browser auto-refresh notifications."""
        async def event_generator():
            while True:
                yield "data: ping\n\n"
                await asyncio.sleep(30)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    @app.get("/preview.pdf")
    async def preview_pdf():
        """Serve compiled PDF using FileResponse."""
        pdf_path = Path(dist_dir) / "resume.pdf"
        if not pdf_path.exists():
            return JSONResponse(
                status_code=404,
                content={"error": "PDF not found. Compile first."}
            )
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename="resume.pdf"
        )

    @app.get("/preview")
    async def preview():
        """HTML page with PDF viewer iframe + SSE listener + error polling."""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Preview</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #16213e;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #0f3460;
        }
        .header h1 {
            font-size: 1.5rem;
            color: #e94560;
        }
        .status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        .status.ready {
            background: #00c853;
            color: #000;
        }
        .status.error {
            background: #ff5252;
            color: #fff;
        }
        .status.compiling {
            background: #ffca28;
            color: #000;
        }
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: currentColor;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 1rem;
            gap: 1rem;
        }
        .pdf-container {
            flex: 1;
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
            min-height: 600px;
        }
        .pdf-container iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        .error-panel {
            background: #2d1f1f;
            border: 1px solid #ff5252;
            border-radius: 8px;
            padding: 1rem;
            display: none;
        }
        .error-panel.visible {
            display: block;
        }
        .error-panel h3 {
            color: #ff5252;
            margin-bottom: 0.5rem;
        }
        .error-panel pre {
            background: #1a1a1a;
            padding: 0.5rem;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 0.85rem;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .log-panel {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 1rem;
            max-height: 150px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.8rem;
        }
        .log-entry {
            margin-bottom: 0.25rem;
        }
        .log-entry.info {
            color: #58a6ff;
        }
        .log-entry.success {
            color: #3fb950;
        }
        .log-entry.error {
            color: #f85149;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📄 Resume Preview</h1>
        <div id="status" class="status ready">
            <div class="status-indicator"></div>
            <span id="status-text">Ready</span>
        </div>
    </div>
    <div class="main-content">
        <div id="error-panel" class="error-panel">
            <h3>⚠️ Compilation Error</h3>
            <pre id="error-message"></pre>
        </div>
        <div class="pdf-container">
            <iframe id="pdf-frame" src="/preview.pdf" title="Resume PDF Preview"></iframe>
        </div>
        <div class="log-panel" id="log-panel">
            <div class="log-entry info">[INFO] Preview server connected</div>
        </div>
    </div>

    <script>
        const statusEl = document.getElementById('status');
        const statusTextEl = document.getElementById('status-text');
        const errorPanel = document.getElementById('error-panel');
        const errorMessage = document.getElementById('error-message');
        const logPanel = document.getElementById('log-panel');
        const pdfFrame = document.getElementById('pdf-frame');

        let lastError = null;
        let compileStatus = 'ready';

        function log(message, type = 'info') {
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            const time = new Date().toLocaleTimeString();
            entry.textContent = `[${time}] ${message}`;
            logPanel.appendChild(entry);
            logPanel.scrollTop = logPanel.scrollHeight;
        }

        function setStatus(status, text) {
            compileStatus = status;
            statusEl.className = `status ${status}`;
            statusTextEl.textContent = text;
        }

        function showError(error) {
            if (error !== lastError) {
                lastError = error;
                errorMessage.textContent = error;
                errorPanel.classList.add('visible');
                log(`Error: ${error}`, 'error');
            }
        }

        function hideError() {
            if (lastError) {
                lastError = null;
                errorPanel.classList.remove('visible');
                log('Error cleared', 'success');
            }
        }

        // SSE Connection for compile events
        function connectSSE() {
            const eventSource = new EventSource('/events');

            eventSource.onopen = () => {
                log('SSE connection established', 'success');
            };

            eventSource.onmessage = (event) => {
                if (event.data === 'compile_complete') {
                    setStatus('ready', 'Compiled Successfully');
                    hideError();
                    pdfFrame.src = '/preview.pdf?' + Date.now();
                    log('Compile complete - refreshing preview', 'success');
                } else if (event.data === 'compile_start') {
                    setStatus('compiling', 'Compiling...');
                    log('Compile started', 'info');
                } else if (event.data === 'compile_error') {
                    setStatus('error', 'Compilation Failed');
                    checkError();
                }
            };

            eventSource.onerror = () => {
                log('SSE connection lost, reconnecting...', 'error');
                eventSource.close();
                setTimeout(connectSSE, 2000);
            };
        }

        // Error polling every 2 seconds
        async function checkError() {
            try {
                const response = await fetch('/error');
                const data = await response.json();
                if (data.last_error) {
                    showError(data.last_error);
                } else {
                    hideError();
                }
            } catch (err) {
                log(`Error polling failed: ${err.message}`, 'error');
            }
        }

        // Initialize
        log('Initializing preview...', 'info');
        connectSSE();
        setInterval(checkError, 2000);
        checkError();
    </script>
</body>
</html>
"""
        return HTMLResponse(content=html_content)

    return app


class PreviewServer:
    """Manages preview server lifecycle."""

    def __init__(
        self,
        port: int = 8000,
        auto_open: bool = True,
        sessions_dir: str = ".sessions",
        inputs_dir: str = "inputs",
        dist_dir: str = "dist"
    ):
        self.port = port
        self.auto_open = auto_open
        self.sessions_dir = Path(sessions_dir)
        self.inputs_dir = Path(inputs_dir)
        self.dist_dir = Path(dist_dir)
        self._server = None
        self._should_exit = False

    def run(self) -> None:
        """Run server. Blocks until stopped."""
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Write PID file
        pid_file = self.sessions_dir / "preview_server.pid"
        pid_file.write_text(str(os.getpid()))

        app = create_app(
            str(self.sessions_dir),
            str(self.inputs_dir),
            str(self.dist_dir)
        )
        config = uvicorn.Config(app, host="127.0.0.1", port=self.port, log_level="warning")
        self._server = uvicorn.Server(config)
        self._server.run()

    def stop(self) -> None:
        """Stop server."""
        if self._server:
            self._server.should_exit = True
