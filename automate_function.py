from pydantic import BaseModel, ConfigDict
from stringcase import camelcase

from specklepy.transports.memory import MemoryTransport
from specklepy.transports.server import ServerTransport
from specklepy.api.operations import receive
from specklepy.api.client import SpeckleClient
from flatten import flatten_base
from speckle_project_data import SpeckleProjectData


class FunctionInputs(BaseModel):
    """
    These are function author defined values, automate will make sure to supply them.
    """

    speckle_type_to_count: str
    model_config = ConfigDict(alias_generator=camelcase)


def automate_function(
    project_data: SpeckleProjectData,
    function_inputs: FunctionInputs,
    speckle_token: str,
):
    client = SpeckleClient(project_data.speckle_server_url)
    client.authenticate_with_token(speckle_token)
    commit = client.commit.get(project_data.project_id, project_data.version_id)

    memory_transport = MemoryTransport()
    server_transport = ServerTransport(project_data.project_id, client)
    if not commit.referencedObject:
        raise ValueError("The commit has no root referencedObject.")

    base = receive(commit.referencedObject, server_transport, memory_transport)

    count = 0
    for b in flatten_base(base):
        if b.speckle_type == function_inputs.speckle_type_to_count:
            count += 1

    print(
        f"Found {count} object that match the queried speckle type: ",
        "{function_inputs.speckle_type_to_count}",
    )
