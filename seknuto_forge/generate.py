"""Replicate generation wrapper. Handles both the photo-reference model
(google/nano-banana-2, IMAGE 1/2/3 inputs) and the text-only print model (ideogram-v2).

image_input entries must be public URLs or data URIs Replicate can fetch. For your
SekTo setup the easiest path is to host before/after/logo on Vercel/S3 and pass URLs.
"""
from __future__ import annotations
from typing import Any
from . import config


def generate(built: dict[str, Any], image_urls: list[str] | None = None,
             resolution: str = "4K", output_format: str = "jpg") -> dict[str, Any]:
    """Run the image model on an assembled prompt.

    built:      output of chassis.build_prompt(...)
    image_urls: [before, after, logo] for nano-banana; [] or None for ideogram.
    Returns {output_url, model, params}.
    """
    import replicate  # lazy import so the package imports without the dep installed

    client = replicate.Client(api_token=config.REPLICATE_API_TOKEN)

    if built["model_hint"] == "image":
        model = config.IMAGE_MODEL  # google/nano-banana-2
        params = {
            "prompt": built["prompt"],
            "aspect_ratio": built["aspect"],
            "resolution": resolution,        # 4K
            "google_search": True,
            "image_search": True,
            "output_format": output_format,  # jpg
        }
        # image_input is optional (schema default []); only send it when we
        # actually have reference URLs, otherwise let nano-banana use its default.
        if image_urls:
            params["image_input"] = image_urls
    else:
        model = config.IMAGE_MODEL_TEXT
        params = {
            "prompt": built["prompt"],
            "aspect_ratio": built["aspect"],
            "magic_prompt_option": "Off",
            "negative_prompt": ", ".join(built["negative"]),
        }

    output = client.run(model, input=params)
    # Replicate returns a URL, a list, or a FileOutput depending on model — normalise.
    url = output[0] if isinstance(output, (list, tuple)) else output
    return {"output_url": str(url), "model": model, "params": params}
