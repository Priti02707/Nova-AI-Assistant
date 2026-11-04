"""Small, bounded JSON client for Nova's configured providers."""

import json
from urllib.request import urlopen


def read_json(request, timeout=5):
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read(256_000))
