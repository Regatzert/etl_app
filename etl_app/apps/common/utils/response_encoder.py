
import base64
from typing import Any


def make_json_safe(value: Any) -> Any:

    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")

    if isinstance(value, dict):
        return {
            key: make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            make_json_safe(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            make_json_safe(item)
            for item in value
        ]

    return value
