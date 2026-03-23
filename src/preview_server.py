import os
import uuid
import time
import threading
import asyncio
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, StreamingResponse
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
