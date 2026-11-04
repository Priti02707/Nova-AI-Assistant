"""Read-only system information for the desktop assistant."""

import platform


def desktop_info():
    return f"{platform.system()} {platform.release()} · {platform.machine()} · Python {platform.python_version()}"
