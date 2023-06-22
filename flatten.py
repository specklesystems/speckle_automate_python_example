from typing import Iterable
from specklepy.objects import Base


def flatten_base(base: Base) -> Iterable[Base]:
    if hasattr(base, "elements"):
        for element in base.elements:
            yield from flatten_base(element)
    yield base