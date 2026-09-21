# vgenv for Python

Official Python client for the [vgenv](https://vgenv.com) AI video generation API: create 4–15 second [MiniMax H3](https://vgenv.com/minimax-h3) videos from text, frames, or reference images, billed per output second. Uses only the standard library.

- [Developer documentation](https://vgenv.com/developers/docs)
- [API pricing](https://vgenv.com/minimax-h3-api)
- [API keys](https://vgenv.com/api-keys)

## Install

```bash
pip install vgenv
```

## Usage

```python
import os
from vgenv import VgenvClient

vgenv = VgenvClient(api_key=os.environ["VGENV_API_KEY"])

video = vgenv.create_video(
    {
        "model": "minimax/h3",
        "tier": "fast",
        "prompt": "A cinematic paper city waking at sunrise, tiny windows lighting up one by one",
        "duration": 5,
        "resolution": "480p",
        "aspect_ratio": "9:16",
    },
    idempotency_key="checkout-item-42",
)

result = vgenv.wait_for_video(video["id"])

if result["status"] == "succeeded":
    print(result["output"]["url"])  # signed URL, store it before it expires
```

Keep your key server-side; never ship it in a browser or mobile bundle. Reuse one `idempotency_key` only for the same logical creation request, and back off on `429` responses using `Retry-After` (the client already does this while polling).

> vgenv is an independent service and is not affiliated with or endorsed by MiniMax.

## License

MIT
