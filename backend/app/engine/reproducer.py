
import shutil
import subprocess
import threading
import time
import uuid

DOCKER_IMAGE = "python:3.12-alpine"
MAX_OUTPUT_BYTES = 1_000_000


def reproduce_bug(code: str, timeout: int = 5) -> dict:
    """Execute submitted Python code in a restricted Docker container."""

    if not shutil.which("docker"):
        return {
            "success": False,
            "stdout": "",
            "stderr": "Docker CLI is not installed or is not in PATH.",
            "returncode": None,
        }

    container_name = f"reproforge-{uuid.uuid4().hex[:12]}"

    python_command = (
        "import sys; "
        "exec(compile(sys.stdin.read(), '<submitted>', 'exec'), "
        "{'__name__': '__main__'})"
    )

    command = [
        "docker", "run", "-i", "--rm",
        "--name", container_name,
        "--network", "none",
        "--memory", "128m",
        "--cpus", "0.5",
        "--pids-limit", "64",
        "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m,mode=1777",
        "--security-opt", "no-new-privileges",
        "--cap-drop", "ALL",
        "--user", "65534:65534",
        "--pull", "never",
        DOCKER_IMAGE,
        "python", "-I", "-c", python_command,
    ]

    process = None
    stdout_parts = []
    stderr_parts = []
    output_size = 0
    output_lock = threading.Lock()
    output_limit_hit = threading.Event()

    def read_stream(stream, parts):
        nonlocal output_size

        try:
            while True:
                chunk = stream.read(4096)
                if not chunk:
                    break

                with output_lock:
                    remaining = MAX_OUTPUT_BYTES - output_size

                    if remaining <= 0:
                        output_limit_hit.set()
                        break

                    kept = chunk[:remaining]
                    output_size += len(kept)
                    parts.append(kept)

                    if len(kept) < len(chunk):
                        output_limit_hit.set()
                        break
        finally:
            stream.close()

    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
        )

        stdout_thread = threading.Thread(
            target=read_stream, args=(process.stdout, stdout_parts), daemon=True
        )
        stderr_thread = threading.Thread(
            target=read_stream, args=(process.stderr, stderr_parts), daemon=True
        )
        stdout_thread.start()
        stderr_thread.start()

        try:
            process.stdin.write(code.encode("utf-8"))
            process.stdin.close()
        except (BrokenPipeError, OSError):
            pass

        deadline = time.monotonic() + timeout + 2

        while process.poll() is None:
            if output_limit_hit.is_set():
                break
            if time.monotonic() >= deadline:
                break
            time.sleep(0.02)

        timed_out = process.poll() is None and not output_limit_hit.is_set()
        limit_hit = output_limit_hit.is_set()

        if timed_out or limit_hit:
            # Stop the container, then stop the Docker CLI if still running.
            try:
                subprocess.run(
                    ["docker", "kill", container_name],
                    capture_output=True,
                    timeout=3,
                    check=False,
                )
            except (subprocess.TimeoutExpired, OSError):
                pass

            if process.poll() is None:
                process.kill()

        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

        stdout_thread.join(timeout=2)
        stderr_thread.join(timeout=2)

        stdout = b"".join(stdout_parts).decode("utf-8", errors="replace")
        stderr = b"".join(stderr_parts).decode("utf-8", errors="replace")

        if limit_hit:
            stderr = "Output limit exceeded (1,000,000 bytes)."
            return {
                "success": False,
                "stdout": stdout,
                "stderr": stderr,
                "returncode": None,
            }

        if timed_out:
            return {
                "success": False,
                "stdout": stdout,
                "stderr": f"Execution timed out after {timeout} seconds.",
                "returncode": None,
            }

        return {
            "success": process.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": process.returncode,
        }

    except OSError:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()

        try:
            subprocess.run(
                ["docker", "kill", container_name],
                capture_output=True,
                timeout=3,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass

        return {
            "success": False,
            "stdout": "",
            "stderr": "Could not start Docker. Check that Docker Desktop is running.",
            "returncode": None,
        }
