import typer
from pydantic import BaseModel
from stringcase import camelcase
from specklepy.transports.memory import MemoryTransport
from specklepy.transports.server import ServerTransport
from specklepy.api.operations import receive
from specklepy.api.client import SpeckleClient
import random

from flatten import flatten_base
from make_comment import make_comment


class SpeckleProjectData(BaseModel):
    """Values of the project / model that triggered the run of this function."""

    project_id: str
    model_id: str
    version_id: str
    speckle_server_url: str

    class Config:
        alias_generator = camelcase


class FunctionInputs(BaseModel):
    """
    These are function author defined values, automate will make sure to supply them.
    """

    comment_text: str

    class Config:
        alias_generator = camelcase


def main(speckle_project_data: str, function_inputs: str, speckle_token: str):
    project_data = SpeckleProjectData.parse_raw(speckle_project_data)
    inputs = FunctionInputs.parse_raw(function_inputs)

    client = SpeckleClient(project_data.speckle_server_url, use_ssl=False)
    client.authenticate_with_token(speckle_token)
    commit = client.commit.get(project_data.project_id, project_data.version_id)
    branch = client.branch.get(project_data.project_id, project_data.model_id, 1)

    memory_transport = MemoryTransport()
    server_transport = ServerTransport(project_data.project_id, client)
    base = receive(commit.referencedObject, server_transport, memory_transport)

    random_beam = random.choice(
        [b for b in flatten_base(base) if b.speckle_type == "IFCBEAM"]
    )

    make_comment(
        client,
        project_data.project_id,
        branch.id,
        project_data.version_id,
        inputs.comment_text,
        random_beam.id,
    )

    print(
        "Ran function with",
        f"{speckle_project_data} {function_inputs}",
    )


if __name__ == "__main__":
    # main(
    #     '{"projectId":"bbb3aba8d4", "modelId":"automateTest", "versionId": "d37ee808db", "speckleServerUrl": "http://hyperion:3000" }',
    #     '{"commentText": "automate made me to do this"}',
    #     "c3e6536e570a94e5d84590c51b29198b26dce89439",
    # )
    typer.run(main)
