# MiniMax H3 Video API examples

Generate 4–15 second MiniMax H3 videos with a small, asynchronous REST API.

[![API status](https://img.shields.io/website?url=https%3A%2F%2Fapi.vgenv.com%2Fv1%2Fstatus&label=API)](https://vgenv.com/status)
[![Docs](https://img.shields.io/badge/docs-v1-b9ff66)](https://vgenv.com/developers/docs)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

- From **$0.0015 per output second** for 480p fast generation
- Text-to-video, first/last-frame video, and ordered reference images
- Standard HTTP and JSON; no SDK dependency
- Idempotent creation, cursor pagination, queue status, and cancellation
- Paid API results are private and watermark-free

> vgenv is an independent service and is not affiliated with or endorsed by MiniMax. `minimax/h3` is a vgenv public model identifier and execution commitment.

## 60-second quickstart

Create an API key at [vgenv API Keys](https://vgenv.com/api-keys), add Project balance, and export the key only in your server-side shell:

```bash
export VGENV_API_KEY="vgenv_live_..."
```

Create a video:

```bash
curl https://api.vgenv.com/v1/videos \
  -H "Authorization: Bearer $VGENV_API_KEY" \
  -H "Idempotency-Key: h3-readme-001" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimax/h3",
    "tier": "fast",
    "prompt": "A cinematic paper city waking at sunrise, tiny windows lighting up one by one",
    "duration": 5,
    "resolution": "480p",
    "aspect_ratio": "9:16"
  }'
```

The API immediately returns a Video resource with an `id`, final price snapshot, and queue state. Poll that resource until it reaches `succeeded`, `failed`, or `cancelled`:

```bash
curl "https://api.vgenv.com/v1/videos/$VIDEO_ID" \
  -H "Authorization: Bearer $VGENV_API_KEY"
```

## Runnable examples

The examples use only standard runtimes and do not save your key to disk.

### Node.js 22+

```bash
node quickstart.mjs
```

### Python 3.11+

```bash
python3 quickstart.py
```

Both programs:

1. submit an idempotent 5-second 480p generation;
2. print the server-authoritative quote;
3. respect `Retry-After` while polling;
4. stop on a terminal status; and
5. print the signed result URL without downloading it automatically.

## Image inputs

Use `frame_images` for a first frame, last frame, or both:

```json
{
  "model": "minimax/h3",
  "prompt": "The paper bird takes flight as the camera slowly pushes in",
  "frame_images": [{
    "type": "image_url",
    "image_url": { "url": "https://example.com/first-frame.webp" },
    "frame_type": "first_frame"
  }]
}
```

Use `reference_images` for up to nine ordered character, product, scene, or style references:

```json
{
  "model": "minimax/h3",
  "prompt": "Keep the product identity from image one and the lighting direction from image two",
  "reference_images": [
    { "type": "image_url", "image_url": { "url": "https://example.com/product.webp" } },
    { "type": "image_url", "image_url": { "url": "https://example.com/lighting.webp" } }
  ]
}
```

Images may be public HTTPS URLs or JPEG/PNG/WebP Data URLs. Each image is limited to 5 MiB. `frame_images` and `reference_images` cannot be combined in one request.

## Production checklist

- Keep `VGENV_API_KEY` on your server; never ship it in a browser or mobile bundle.
- Reuse one `Idempotency-Key` only for the same logical creation request.
- Treat `price`, supported configurations, and task state as server-authoritative.
- Back off on `429` responses using the `Retry-After` header.
- Store completed output before its signed URL expires.
- Handle `failed` and `cancelled` as terminal states; platform failures release reserved balance.

## API resources

- [MiniMax H3 API landing page](https://vgenv.com/minimax-h3-api)
- [Developer documentation](https://vgenv.com/developers/docs)
- [Live API status](https://vgenv.com/status)
- [Interactive OpenAPI](https://api.vgenv.com/docs)
- [Free MiniMax H3 generator](https://vgenv.com/minimax-h3)

## 中文说明

本仓库提供可直接运行的 MiniMax H3 REST API 示例。API 按生成秒数计费，创建时返回最终报价并冻结余额；成功后结算，平台失败或排队取消时释放冻结金额。完整字段、图片输入规则和错误码请查看[中文开发者文档](https://vgenv.com/developers/docs)。
