// Official client for the vgenv AI video generation API.
// Thin wrapper over the documented REST surface: https://vgenv.com/developers/docs

const DEFAULT_BASE_URL = "https://api.vgenv.com/v1";
const TERMINAL_STATUSES = new Set(["succeeded", "failed", "cancelled"]);

const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

export class VgenvError extends Error {
  constructor(status, payload, retryAfter) {
    super(payload?.message ?? `vgenv API request failed with HTTP ${status}`);
    this.name = "VgenvError";
    this.status = status;
    this.payload = payload;
    this.retryAfter = retryAfter;
  }
}

export class VgenvClient {
  constructor({ apiKey, baseUrl = DEFAULT_BASE_URL } = {}) {
    if (!apiKey) {
      throw new TypeError("vgenv: apiKey is required. Create one at https://vgenv.com/api-keys");
    }
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async #request(path, { method = "GET", body, headers } = {}) {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        ...(body ? { "Content-Type": "application/json" } : {}),
        ...headers,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      throw new VgenvError(response.status, payload, Number(response.headers.get("retry-after")) || null);
    }
    return payload;
  }

  // Reuse one Idempotency-Key only for the same logical creation request.
  createVideo(input, { idempotencyKey } = {}) {
    return this.#request("/videos", {
      method: "POST",
      body: input,
      headers: idempotencyKey ? { "Idempotency-Key": idempotencyKey } : {},
    });
  }

  getVideo(videoId) {
    return this.#request(`/videos/${encodeURIComponent(videoId)}`);
  }

  async waitForVideo(videoId, { pollIntervalMs = 8_000, timeoutMs = 30 * 60_000, onProgress } = {}) {
    const deadline = Date.now() + timeoutMs;
    let current = await this.getVideo(videoId);
    while (!TERMINAL_STATUSES.has(current.status)) {
      if (Date.now() >= deadline) throw new Error(`Timed out waiting for video ${videoId}`);
      await sleep(pollIntervalMs);
      try {
        current = await this.getVideo(videoId);
      } catch (error) {
        if (!(error instanceof VgenvError) || error.status !== 429) throw error;
        await sleep((error.retryAfter ?? 10) * 1_000);
        continue;
      }
      onProgress?.(current);
    }
    return current;
  }
}

export default VgenvClient;
