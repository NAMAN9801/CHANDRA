import shutil
import socket
import subprocess
import time
from urllib.request import urlopen

import pytest


def _find_open_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.mark.smoke
def test_docker_image_starts_and_health_endpoint_works():
    if shutil.which("docker") is None:
        pytest.skip("docker is not available in this environment")

    tag = "chandra-smoke:test"
    host_port = _find_open_port()

    subprocess.run(["docker", "build", "-t", tag, "."], check=True)
    run_proc = subprocess.run(
        ["docker", "run", "-d", "-p", f"{host_port}:5000", tag],
        check=True,
        capture_output=True,
        text=True,
    )
    container_id = run_proc.stdout.strip()

    try:
        deadline = time.time() + 30
        last_err = None
        while time.time() < deadline:
            try:
                with urlopen(f"http://127.0.0.1:{host_port}/health", timeout=2) as response:
                    body = response.read().decode("utf-8")
                    assert response.status == 200
                    assert '"status":"ok"' in body.replace(" ", "")
                    return
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                time.sleep(1)
        raise AssertionError(f"container did not become healthy in time: {last_err}")
    finally:
        subprocess.run(["docker", "rm", "-f", container_id], check=False)
