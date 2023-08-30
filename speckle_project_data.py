from pydantic import BaseModel, ConfigDict
from stringcase import camelcase


class SpeckleProjectData(BaseModel):
    """Values of the project / model that triggered the run of this function."""

    project_id: str
    model_id: str
    version_id: str
    speckle_server_url: str

    model_config = ConfigDict(alias_generator=camelcase, protected_namespaces=())
