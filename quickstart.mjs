const API_BASE_URL = (process.env.VGENV_API_BASE_URL ?? "https://api.vgenv.com/v1").replace(/\/$/, "");
const API_KEY = process.env.VGENV_API_KEY;
const MAX_WAIT_MS = 30 * 60 * 1_000;

if (!API_KEY) {
  console.error("Set VGENV_API_KEY before running this example.");
  process.exit(1);
}

const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

async function request(path, init = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...init.headers,
    },
  });
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(payload?.message ?? `Request failed with HTTP ${response.status}`);
    error.status = response.status;
    error.retryAfter = Number(response.headers.get("retry-after")) || null;
    error.payload = payload;
    throw error;
  }
  return payload;
}

async function main() {
  const idempotencyKey = `node-quickstart-${crypto.randomUUID()}`;
  const video = await request("/videos", {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
    body: JSON.stringify({
      model: "minimax/h3",
      tier: "fast",
      prompt: "A cinematic paper city waking at sunrise, tiny windows lighting up one by one",
      duration: 5,
      resolution: "480p",
      aspect_ratio: "9:16",
    }),
  });

  console.log("Created:", video.id);
  console.log("Quote:", video.price);

  const deadline = Date.now() + MAX_WAIT_MS;
  let current = video;
  while (!["succeeded", "failed", "cancelled"].includes(current.status)) {
    if (Date.now() >= deadline) throw new Error(`Timed out waiting for ${video.id}`);
    await sleep(8_000);
    try {
      current = await request(`/videos/${encodeURIComponent(video.id)}`);
      console.log(`${current.status}: ${current.progress}%`);
    } catch (error) {
      if (error.status !== 429) throw error;
      await sleep((error.retryAfter ?? 10) * 1_000);
    }
  }

  if (current.status !== "succeeded") {
    throw new Error(`Generation ended as ${current.status}: ${JSON.stringify(current.error)}`);
  }
  console.log("Result URL:", current.output.url);
  console.log("Expires at:", current.output.expires_at);
}

main().catch((error) => {
  console.error(error.payload ?? error);
  process.exitCode = 1;
});
