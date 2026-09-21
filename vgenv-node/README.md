# vgenv for Node.js

Official Node.js client for the [vgenv](https://vgenv.com) AI video generation API: create 4–15 second [MiniMax H3](https://vgenv.com/minimax-h3) videos from text, frames, or reference images, billed per output second. Zero runtime dependencies.

- [Developer documentation](https://vgenv.com/developers/docs)
- [API pricing](https://vgenv.com/minimax-h3-api)
- [API keys](https://vgenv.com/api-keys)

## Install

```bash
npm install vgenv
```

## Usage

```js
import { VgenvClient } from "vgenv";

const vgenv = new VgenvClient({ apiKey: process.env.VGENV_API_KEY });

const video = await vgenv.createVideo(
  {
    model: "minimax/h3",
    tier: "fast",
    prompt: "A cinematic paper city waking at sunrise, tiny windows lighting up one by one",
    duration: 5,
    resolution: "480p",
    aspect_ratio: "9:16",
  },
  { idempotencyKey: "checkout-item-42" },
);

const result = await vgenv.waitForVideo(video.id, {
  onProgress: (current) => console.log(`${current.status}: ${current.progress}%`),
});

if (result.status === "succeeded") {
  console.log(result.output.url); // signed URL, store it before it expires
}
```

Keep your key server-side; never ship it in a browser or mobile bundle. Reuse one `Idempotency-Key` only for the same logical creation request, and back off on `429` responses using `Retry-After` (the client already does this while polling).

> vgenv is an independent service and is not affiliated with or endorsed by MiniMax.

## License

MIT
