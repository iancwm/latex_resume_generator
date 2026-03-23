import os
import uuid
import time
import threading
from pathlib import Path
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
import uvicorn


def create_app(sessions_dir: str, inputs_dir: str, dist_dir: str) -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(title="Resume Preview Server")

    server_id = str(uuid.uuid4())
    started_at = time.time()

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
