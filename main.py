import typer
import os
from speckle_project_data import SpeckleProjectData
from automate_function import FunctionInputs, automate_function


def main(speckle_project_data: str, function_inputs: str, speckle_token: str = ""):
    speckle_token = speckle_token if speckle_token else os.environ.get("SPECKLE_TOKEN")
    if not speckle_token:
        raise ValueError("The supplied speckle token is not valid")

    project_data = SpeckleProjectData.model_validate_json(speckle_project_data)
    inputs = FunctionInputs.model_validate_json(function_inputs)
    automate_function(project_data, inputs, speckle_token)


if __name__ == "__main__":
    typer.run(main)
