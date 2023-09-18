"""This module contains the business logic of the function.

Make sure that this module exposes a `FunctionInputs` class
and an `automate_function` function definition.
"""
from specklepy.objects.geometry import Mesh

from automate_sdk import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)
from flatten import flatten_base


class FunctionInputs(AutomateBase):
    """These are function author defined values.

    Automate will make sure to supply them matching the types specified here.
    """

    forbidden_speckle_type: str


def automate_function(
    automate_context: AutomationContext,
    function_inputs: FunctionInputs,
) -> None:
    """Hey, trying the automate sdk experience here."""
    version_root_object = automate_context.receive_version()

    count = 0
    for b in flatten_base(version_root_object):
        if b.speckle_type == function_inputs.forbidden_speckle_type:
            if not b.id:
                raise ValueError("Cannot operate on objects without their id's.")
            automate_context.add_object_error(
                b.id,
                "This project should not contain the type: "
                f"{function_inputs.forbidden_speckle_type}",
            )
            count += 1

    if count > 0:
        automate_context.mark_run_failed(
            "Automation failed: "
            f"Found {count} object that have a forbidden speckle type: "
            f"{function_inputs.forbidden_speckle_type}"
        )

    else:
        automate_context.mark_run_success("No forbidden types found.")


if __name__ == "__main__":
    execute_automate_function(automate_function, FunctionInputs)
