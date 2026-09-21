"""Official client for the vgenv AI video generation API.

Thin wrapper over the documented REST surface: https://vgenv.com/developers/docs
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://api.vgenv.com/v1"
TERMINAL_STATUSES = frozenset({"succeeded", "failed", "cancelled"})

__version__ = "0.1.0"
__all__ = ["VgenvClient", "VgenvError"]


class VgenvError(RuntimeError):
    def __init__(self, status, payload, retry_after=None):
        super().__init__(f"HTTP {status}: {payload}")
        self.status = status
        self.payload = payload
        self.retry_after = retry_after


class VgenvClient:
    def __init__(self, api_key, base_url=DEFAULT_BASE_URL):
        if not api_key:
            raise ValueError("api_key is required. Create one at https://vgenv.com/api-keys")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _request(self, path, *, method="GET", body=None, headers=None):
        encoded = json.dumps(body).encode("utf-8") if body is not None else None
        request_headers = {"Authorization": f"Bearer {self.api_key}", **(headers or {})}
        if encoded is not None:
            request_headers["Content-Type"] = "application/json"
        req = urllib.request.Request(f"{self.base_url}{path}", data=encoded, headers=request_headers, method=method)
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
            raise VgenvError(error.code, payload, retry_after) from error

    def create_video(self, payload, *, idempotency_key=None):
        """Create a Video generation. Reuse one idempotency_key only for the same logical request."""
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None
        return self._request("/videos", method="POST", body=payload, headers=headers)

    def get_video(self, video_id):
        """Fetch a Video resource by id, including status, progress, and price."""
        return self._request(f"/videos/{video_id}")

    def wait_for_video(self, video_id, *, poll_interval_seconds=8, timeout_seconds=1800, on_progress=None):
        """Poll until the Video reaches a terminal status; returns the final Video resource."""
        deadline = time.monotonic() + timeout_seconds
        current = self.get_video(video_id)
        while current["status"] not in TERMINAL_STATUSES:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Timed out waiting for video {video_id}")
            time.sleep(poll_interval_seconds)
            try:
                current = self.get_video(video_id)
            except VgenvError as error:
                if error.status != 429:
                    raise
                time.sleep(error.retry_after or 10)
                continue
            if on_progress:
                on_progress(current)
        return current
