"""Helper module for a simple speckle object tree flattening."""

from collections.abc import Iterable

from specklepy.objects import Base


def flatten_base(base: Base) -> Iterable[Base]:
    """Flatten a base object into an iterable of bases.
    
    This function recursively traverses the `elements` or `@elements` attribute of the 
    base object, yielding each nested base object.

    Args:
        base (Base): The base object to flatten.

    Yields:
        Base: Each nested base object in the hierarchy.
    """
    # Attempt to get the elements attribute, fallback to @elements if necessary
    elements = getattr(base, "elements", getattr(base, "@elements", None))
    
    if elements is not None:
        for element in elements:
            yield from flatten_base(element)
    
    yield base
