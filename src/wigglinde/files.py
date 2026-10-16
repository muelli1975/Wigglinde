"""Local file replacement for completed exports."""
from pathlib import Path
import time


def _replace_with_retry(source: Path, target: Path) -> None:
    for attempt in range(5):
        try:
            source.replace(target)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.1)
