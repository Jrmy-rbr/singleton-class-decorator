from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Cache:
    is_singleton: bool
    already_created: bool = False
    obj: Optional[Any] = None
    args: Optional[Any] = None
    kwargs: Optional[Any] = None
