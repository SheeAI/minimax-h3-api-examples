"""Minimal MiniMax H3 API example using only the Python standard library."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid

API_BASE_URL = os.getenv("VGENV_API_BASE_URL", "https://api.vgenv.com/v1").rstrip("/")
API_KEY = os.getenv("VGENV_API_KEY")
TERMINAL_STATUSES = {"succeeded", "failed", "cancelled"}


class ApiError(RuntimeError):
    def __init__(self, status: int, payload: object, retry_after: int | None = None):
        super().__init__(f"HTTP {status}: {payload}")
        self.status = status
        self.payload = payload
        self.retry_after = retry_after


def request(path: str, *, method: str = "GET", body: dict | None = None, headers: dict | None = None) -> dict:
    encoded = json.dumps(body).encode("utf-8") if body is not None else None
    request_headers = {"Authorization": f"Bearer {API_KEY}", **(headers or {})}
    if encoded is not None:
        request_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{API_BASE_URL}{path}", data=encoded, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = raw
        retry_after = int(error.headers["Retry-After"]) if error.headers.get("Retry-After", "").isdigit() else None
        raise ApiError(error.code, payload, retry_after) from error


def main() -> None:
    if not API_KEY:
        raise SystemExit("Set VGENV_API_KEY before running this example.")

    video = request(
        "/videos",
        method="POST",
        headers={"Idempotency-Key": f"python-quickstart-{uuid.uuid4()}"},
        body={
            "model": "minimax/h3",
            "tier": "fast",
            "prompt": "A cinematic paper city waking at sunrise, tiny windows lighting up one by one",
            "duration": 5,
            "resolution": "480p",
            "aspect_ratio": "9:16",
        },
    )
    print("Created:", video["id"])
    print("Quote:", video["price"])

    deadline = time.monotonic() + 30 * 60
    current = video
    while current["status"] not in TERMINAL_STATUSES:
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Timed out waiting for {video['id']}")
        time.sleep(8)
        try:
            current = request(f"/videos/{video['id']}")
            print(f"{current['status']}: {current['progress']}%")
        except ApiError as error:
            if error.status != 429:
                raise
            time.sleep(error.retry_after or 10)

    if current["status"] != "succeeded":
        raise RuntimeError(f"Generation ended as {current['status']}: {current.get('error')}")
    print("Result URL:", current["output"]["url"])
    print("Expires at:", current["output"]["expires_at"])


if __name__ == "__main__":
    main()
