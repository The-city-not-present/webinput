#!/usr/bin/env python3
"""Cross-platform developer tooling for the webinput dev backend (localhost:5279).

webinput is a one-shot library (`answer = webinput(...)`), so it has no
naturally-running backend. The Vite dev server for its Vue skin, however, needs
a stable headless backend to proxy to — this script is that backend's single
source of truth, mirroring the parent gitgui project's ``dev_backend.py``.

Usage:
    python dev_webinput.py status   [--port N] [--json]
    python dev_webinput.py start    [--port N]
    python dev_webinput.py stop     [--port N]
    python dev_webinput.py restart  [--port N]
    python dev_webinput.py health   [--port N] [--json]
    python dev_webinput.py logs     [--lines N]

``start`` runs webinput headlessly with ``keep_alive=True`` (serve until
stopped — no browser, no auto-shutdown after a POST) on a fixed port, so the
Vite dev server's proxy target stays honest.

Exit codes: 0 = success / healthy / running, 1 = error / not running.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from http.client import HTTPConnection
from pathlib import Path

DEFAULT_PORT = 5279
PID_FILE_NAME = ".webinput-dev-backend.pid"
LOG_FILE_NAME = ".webinput-dev-backend.log"
HEALTH_PATH = "/health"
HEALTH_TIMEOUT_SECONDS = 2.0
START_WAIT_SECONDS = 15.0
START_POLL_SECONDS = 0.25

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def _colors_enabled() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            stdout_handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(stdout_handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(stdout_handle, mode.value | 0x0004)
        except Exception:
            pass
    return True


def _paint(text: str, color: str) -> str:
    return f"{color}{text}{RESET}" if _colors_enabled() else text


def _success(text: str) -> str:
    return _paint(text, GREEN)


def _error(text: str) -> str:
    return _paint(text, RED)


def repo_root() -> Path:
    """Directory this script lives in (the webinput root)."""
    return Path(__file__).resolve().parent


def venv_python(root: Path | None = None) -> str | None:
    root = root or repo_root()
    for rel in (".venv/Scripts/python.exe", ".venv/bin/python"):
        candidate = root / rel
        if candidate.is_file():
            return str(candidate)
    return None


def pid_file_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / PID_FILE_NAME


def log_file_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / LOG_FILE_NAME


def read_pid(root: Path | None = None) -> int | None:
    try:
        text = pid_file_path(root).read_text(encoding="utf-8").strip()
        return int(text) if text else None
    except (OSError, ValueError):
        return None


def write_pid(pid: int, root: Path | None = None) -> None:
    pid_file_path(root).write_text(f"{pid}\n", encoding="utf-8")


def remove_pid(root: Path | None = None) -> None:
    try:
        pid_file_path(root).unlink()
    except OSError:
        pass


def pid_is_alive(pid: int) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True, text=True, timeout=5,
            )
            return str(pid) in result.stdout
        except (OSError, subprocess.SubprocessError):
            return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except (PermissionError, OSError):
        return True
    return True


def is_healthy(
    port: int = DEFAULT_PORT,
    path: str = HEALTH_PATH,
    timeout: float = HEALTH_TIMEOUT_SECONDS,
) -> tuple[bool, str]:
    """HTTP probe: webinput's /health answers 200 only for HEAD (else 405)."""
    last_error = "no connection attempted"
    for host in ("localhost", "127.0.0.1"):
        connection = HTTPConnection(host, port, timeout=timeout)
        try:
            connection.request("HEAD", path)
            response = connection.getresponse()
            response.read()
            if response.status == 200:
                return True, f"HTTP 200 ({host})"
            return False, f"HTTP {response.status} (expected 200)"
        except OSError as exc:
            last_error = f"{host}: {exc}"
        finally:
            connection.close()
    return False, last_error
def find_pids_on_port(port: int) -> list[int]:
    pids: list[int] = []
    if os.name == "nt":
        try:
            out = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True, text=True, timeout=10,
            ).stdout
        except (OSError, subprocess.SubprocessError):
            return pids
        for line in out.splitlines():
            if "LISTENING" not in line.upper():
                continue
            tokens = line.split()
            if len(tokens) < 2:
                continue
            if tokens[1].endswith(f":{port}"):
                try:
                    pids.append(int(tokens[-1]))
                except (ValueError, IndexError):
                    pass
    else:
        try:
            out = subprocess.run(
                ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
                capture_output=True, text=True, timeout=10,
            ).stdout
        except (OSError, subprocess.SubprocessError):
            return pids
        for line in out.splitlines():
            line = line.strip()
            if line.isdigit():
                pids.append(int(line))
    return sorted(set(pids))


def terminate_pid(pid: int) -> None:
    if pid <= 0:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True, timeout=10,
        )
        return
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.kill(pid, sig)
        except OSError:
            return
        for _ in range(50):
            if not pid_is_alive(pid):
                return
            time.sleep(0.1)
def stop_backend(port: int = DEFAULT_PORT, root: Path | None = None) -> tuple[bool, str]:
    messages: list[str] = []
    stopped = False

    pid = read_pid(root)
    if pid is not None:
        if pid_is_alive(pid):
            terminate_pid(pid)
            stopped = True
            messages.append(f"stopped pid {pid} (from pid file)")
        remove_pid(root)

    for candidate in find_pids_on_port(port):
        if candidate == os.getpid():
            continue
        terminate_pid(candidate)
        stopped = True
        messages.append(f"stopped pid {candidate} (listening on port {port})")

    if not stopped:
        messages.append("backend was not running")
    return stopped, "; ".join(messages)


def _spawn(command: list[str], root: Path) -> subprocess.Popen:
    log_handle = open(log_file_path(root), "a", encoding="utf-8")
    kwargs = {
        "cwd": str(root),
        "stdout": log_handle,
        "stderr": subprocess.STDOUT,
        "start_new_session": os.name != "nt",
    }
    if os.name == "nt":
        kwargs["creationflags"] = (
            subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    try:
        return subprocess.Popen(command, **kwargs)
    finally:
        log_handle.close()


def start_backend(
    port: int = DEFAULT_PORT,
    root: Path | None = None,
    wait: float = START_WAIT_SECONDS,
) -> tuple[bool, str]:
    root = root or repo_root()

    python = venv_python(root)
    if not python:
        return False, "no venv found — run ./build.sh once to create .venv and install deps"

    healthy, detail = is_healthy(port)
    if healthy:
        return True, f"already running on port {port} ({detail})"

    for candidate in find_pids_on_port(port):
        if candidate != os.getpid():
            terminate_pid(candidate)

    command = [python, str(Path(__file__).resolve()), "_serve", "--port", str(port)]
    process = _spawn(command, root)
    write_pid(process.pid, root)

    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        healthy, detail = is_healthy(port)
        if healthy:
            return True, f"started pid {process.pid} on http://localhost:{port} ({detail})"
        if process.poll() is not None:
            remove_pid(root)
            return False, (
                f"webinput backend pid {process.pid} exited early with code "
                f"{process.returncode}; see `python dev_webinput.py logs`"
            )
        time.sleep(START_POLL_SECONDS)

    return False, (
        f"webinput backend pid {process.pid} did not become healthy on port {port} "
        f"within {wait:.0f}s; see `python dev_webinput.py logs`"
    )


def backend_status(port: int = DEFAULT_PORT, root: Path | None = None) -> dict:
    pid = read_pid(root)
    healthy, detail = is_healthy(port)
    return {
        "port": port,
        "pid": pid,
        "pid_alive": pid_is_alive(pid) if pid is not None else False,
        "healthy": healthy,
        "detail": detail,
        "listeners": find_pids_on_port(port),
        "running": healthy,
    }


def _print_status(status: dict, as_json: bool) -> int:
    if as_json:
        print(json.dumps(status, indent=2))
    else:
        state = "running/healthy" if status["healthy"] else "not running"
        line = f"port {status['port']}: {state}"
        print(_success(line) if status["healthy"] else _error(line))
        print(f"  pid: {status['pid']} (alive: {status['pid_alive']})")
        print(f"  health: {status['detail']}")
        if status["listeners"]:
            print(f"  listeners: {status['listeners']}")
    return 0 if status["healthy"] else 1
def serve(port: int) -> None:
    """Run webinput headlessly on ``port`` until stopped (internal verb)."""
    # `webinput` is the package rooted at this script's directory; it becomes
    # importable only when its *parent* directory is on sys.path. Add it here so
    # the subprocess works regardless of the process cwd.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    from webinput import (
        webinput,
        QuestionTypeRoot,
        QuestionTypeSinglePunch,
        Category,
    )

    form = QuestionTypeRoot(
        label='Project selector (dev)',
        fields=[
            QuestionTypeSinglePunch(
                name='project',
                label='Please select a project to open',
                categories=[
                    Category(name='alpha', label='Project Alpha'),
                    Category(name='beta', label='Project Beta'),
                ],
            ),
        ],
    )
    webinput(form, {
        'keep_alive': True,
        'http_host': 'localhost',
        'http_port': port,
        'skin': 'vue',
    })


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dev_webinput.py",
        description=f"Manage the webinput dev backend (localhost:{DEFAULT_PORT}).",
    )
    parser.add_argument(
        "command",
        choices=["status", "start", "stop", "restart", "health", "logs", "_serve"],
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--lines", type=int, default=50)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    command = args.command

    if command == "_serve":
        serve(args.port)
        return 0

    if command == "status":
        return _print_status(backend_status(args.port), args.json)

    if command == "health":
        healthy, detail = is_healthy(args.port)
        if args.json:
            print(json.dumps({"port": args.port, "healthy": healthy, "detail": detail}))
        else:
            message = (
                f"port {args.port}: "
                + ("healthy (HTTP 200)" if healthy else f"unhealthy — {detail}")
            )
            print(_success(message) if healthy else _error(message))
        return 0 if healthy else 1

    if command == "start":
        ok, message = start_backend(args.port)
        print(_success(message) if ok else _error(message))
        return 0 if ok else 1

    if command == "stop":
        stopped, message = stop_backend(args.port)
        print(_success(message) if stopped else message)
        return 0

    if command == "restart":
        stop_backend(args.port)
        time.sleep(0.3)
        ok, message = start_backend(args.port)
        print(_success(message) if ok else _error(message))
        return 0 if ok else 1

    if command == "logs":
        try:
            lines = log_file_path().read_text(encoding="utf-8").splitlines()
        except OSError:
            print(_error(f"no log file at {log_file_path()}"))
            return 1
        print("\n".join(lines[-args.lines:]) if lines else "(empty log)")
        return 0

    build_parser().error(f"unknown command: {command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
