"""WIP module for an automate python sdk."""
import json
import os
import sys
import time
import traceback
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, TypeVar, overload

import httpx
from gql import gql
from pydantic import BaseModel, ConfigDict
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.objects.base import Base
from specklepy.transports.memory import MemoryTransport
from specklepy.transports.server import ServerTransport
from stringcase import camelcase


class AutomateBase(BaseModel):
    """Use this class as a base model for automate related DTO."""

    model_config = ConfigDict(alias_generator=camelcase, populate_by_name=True)


class AutomationRunData(BaseModel):
    """Values of the project / model that triggered the run of this function."""

    project_id: str
    model_id: str
    branch_name: str
    version_id: str
    speckle_server_url: str

    automation_id: str
    automation_revision_id: str
    automation_run_id: str

    function_id: str
    function_revision: str

    model_config = ConfigDict(
        alias_generator=camelcase, populate_by_name=True, protected_namespaces=()
    )


class AutomationStatus(str, Enum):
    """Set the status of the automation."""

    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"


class ObjectResultLevel(str, Enum):
    """Possible status message levels for object reports."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ObjectResult(AutomateBase):
    """An object level result."""

    level: ObjectResultLevel
    status_message: str


class AutomationResult(AutomateBase):
    """Schema accepted by the Speckle server as a result for an automation run."""

    elapsed: float = 0
    result_view: str | None = None
    result_versions: list[str] = field(default_factory=list)
    blobs: list[str] = field(default_factory=list)
    run_status: AutomationStatus = AutomationStatus.RUNNING
    status_message: str | None = None

    object_results: dict[str, list[ObjectResult]] = field(
        default_factory=lambda: defaultdict(list)  # typing: ignore
    )


T = TypeVar("T", bound=AutomateBase)


@dataclass
class AutomationContext:
    """A WIP umbrella class for automate sdk functionality.

    Potentially turn this into a context manager, to handle function enter exit status
    changes.
    """

    automation_run_data: AutomationRunData
    speckle_client: SpeckleClient
    _server_transport: ServerTransport
    _speckle_token: str

    #: keep a memory transponrt at hand, to speed up things if needed
    _memory_transport: MemoryTransport = field(default_factory=MemoryTransport)

    #: added for performance measuring
    _init_time: float = field(default_factory=time.perf_counter)
    _automation_result: AutomationResult = field(default_factory=AutomationResult)

    @classmethod
    def initialize(
        cls, automation_run_data: str | AutomationRunData, speckle_token: str
    ) -> "AutomationContext":
        """Bootstrap the AutomateSDK from raw data.

        Todo:
        ----
            * bootstrap a structlog logger instance
            * expose a logger, that ppl can use instead of print
            * log an initialization message
        """
        # parse the json value if its not an initialized project data instance
        automation_run_data = (
            automation_run_data
            if isinstance(automation_run_data, AutomationRunData)
            else AutomationRunData.model_validate_json(automation_run_data)
        )
        speckle_client = SpeckleClient(
            automation_run_data.speckle_server_url,
            automation_run_data.speckle_server_url.startswith("https"),
        )
        speckle_client.authenticate_with_token(speckle_token)
        if not speckle_client.account:
            msg = (
                f"Could not autenticate to {automation_run_data.speckle_server_url}",
                "with the provided token",
            )
            raise ValueError(msg)
        server_transport = ServerTransport(
            automation_run_data.project_id, speckle_client
        )
        return cls(automation_run_data, speckle_client, server_transport, speckle_token)

    @property
    def run_status(self) -> AutomationStatus:
        """Get the status of the automation run."""
        return self._automation_result.run_status

    def elapsed(self) -> float:
        """Return the elapsed time in seconds since the initialization time."""
        return time.perf_counter() - self._init_time

    def receive_version(self) -> Base:
        """Receive the Speckle project version that triggered this automation run."""
        commit = self.speckle_client.commit.get(
            self.automation_run_data.project_id, self.automation_run_data.version_id
        )
        if not commit.referencedObject:
            raise ValueError("The commit has no referencedObject, cannot receive it.")
        base = operations.receive(
            commit.referencedObject, self._server_transport, self._memory_transport
        )
        print(
            f"It took {self.elapsed():2f} seconds to receive",
            f" the speckle version {self.automation_run_data.version_id}",
        )
        return base

    def create_new_version_in_project(
        self, root_object: Base, model_id: str, version_message: str = ""
    ) -> None:
        """Save a base model to a new version on the project.

        Args:
            root_object (Base): The Speckle base object for the new version.
            model_id (str): For now please use a `branchName`!
            version_message (str): The message for the new version.
        """
        if model_id == self.automation_run_data.model_id:
            raise ValueError(
                f"The target model id: {model_id} cannot match the model id"
                f" that triggered this automation: {self.automation_run_data.model_id}"
            )

        root_object_id = operations.send(
            root_object,
            [self._server_transport, self._memory_transport],
            use_default_cache=False,
        )

        version_id = self.speckle_client.commit.create(
            stream_id=self.automation_run_data.project_id,
            object_id=root_object_id,
            branch_name=model_id,
            message=version_message,
            source_application="SpeckleAutomate",
        )
        self._automation_result.result_versions.append(version_id)

    def report_run_status(self) -> None:
        """Report the current run status to the Speckle server triggered the automation.

        Once the automation function exits, send the status  to the speckle server.
        Return the result from the server, it should be a link to the stored automation
        result.
        """
        query = gql(
            """
            mutation ReportFunctionRunStatus(
                $automationId: String!, 
                $automationRevisionId: String!, 
                $automationRunId: String!,
                $versionId: String!,
                $functionId: String!,
                $runStatus: AutomationRunStatus!
                $elapsed: Float!
                $resultVersionIds: [String!]!
                $statusMessage: String
                $objectResults: JSONObject
            ){
                automationMutations {
                    functionRunStatusReport(input: {
                        automationId: $automationId
                        automationRevisionId: $automationRevisionId
                        automationRunId: $automationRunId
                        versionId: $versionId
                        functionRuns: [
                        {
                            functionId: $functionId
                            status: $runStatus,
                            elapsed: $elapsed,
                            resultVersionIds: $resultVersionIds,
                            statusMessage: $statusMessage
                            results: $objectResults
                        }]
                   })
                }
            }
            """
        )
        if self.run_status in [AutomationStatus.SUCCEEDED, AutomationStatus.FAILED]:
            object_results = {
                "version": "1.0.0",
                "values": {
                    "speckleObjects": self._automation_result.model_dump(by_alias=True)[
                        "objectResults"
                    ],
                    "blobs": self._automation_result.blobs,
                },
            }
        else:
            object_results = None
        params = {
            "automationId": self.automation_run_data.automation_id,
            "automationRevisionId": self.automation_run_data.automation_revision_id,
            "automationRunId": self.automation_run_data.automation_run_id,
            "versionId": self.automation_run_data.version_id,
            "functionId": self.automation_run_data.function_id,
            "runStatus": self.run_status.value,
            "elapsed": self.elapsed(),
            "resultVersionIds": self._automation_result.result_versions,
            "objectResults": object_results,
        }
        self.speckle_client.httpclient.execute(query, params)

    def store_file_result(self, file_path: Path | str) -> None:
        """Save a file attached to the project of this automation."""
        path_obj = (
            Path(file_path).resolve() if isinstance(file_path, str) else file_path
        )

        class UploadResult(AutomateBase):
            blob_id: str
            file_name: str
            upload_status: int

        class BlobUploadResponse(AutomateBase):
            upload_results: list[UploadResult]

        if not path_obj.exists():
            raise ValueError("The given file path doesn't exist")
        files = {path_obj.name: open(str(path_obj), "rb")}

        url = (
            f"{self.automation_run_data.speckle_server_url}/api/stream/"
            f"{self.automation_run_data.project_id}/blob"
        )
        data = (
            httpx.post(
                url,
                files=files,
                headers={"authorization": f"Bearer {self._speckle_token}"},
            )
            .raise_for_status()
            .json()
        )

        upload_response = BlobUploadResponse.model_validate(data)

        if len(upload_response.upload_results) != 1:
            raise ValueError("Expecting one upload result.")

        for upload_result in upload_response.upload_results:
            self._automation_result.blobs.append(upload_result.blob_id)

    def mark_run_failed(self, status_message: str) -> None:
        """Mark the current run a failure."""
        self._mark_run(AutomationStatus.FAILED, status_message)

    def mark_run_success(self, status_message: str | None) -> None:
        """Mark the current run a success with an optional message."""
        self._mark_run(AutomationStatus.SUCCEEDED, status_message)

    def _mark_run(self, status: AutomationStatus, status_message: str | None) -> None:
        duration = self.elapsed()
        self._automation_result.status_message = status_message
        self._automation_result.run_status = status
        self._automation_result.elapsed = duration

        msg = f"Automation run {status.value} after {duration:2f} seconds."
        print("\n".join([msg, status_message]) if status_message else msg)

    def add_object_error(self, object_id: str, error_cause: str) -> None:
        """Add an error to a given objec id."""
        self._add_object_result(object_id, ObjectResultLevel.ERROR, error_cause)

    def add_object_warning(self, object_id: str, warning: str) -> None:
        """Add a warning to a given object id."""
        self._add_object_result(object_id, ObjectResultLevel.WARNING, warning)

    def add_object_info(self, object_id: str, info: str) -> None:
        """Add an info message to a given object."""
        self._add_object_result(object_id, ObjectResultLevel.INFO, info)

    def _add_object_result(
        self, object_id: str, level: ObjectResultLevel, status_message: str
    ) -> None:
        print(
            f"Object {object_id} was marked with {level.value.upper()}",
            f" cause: {status_message}",
        )
        self._automation_result.object_results[object_id].append(
            ObjectResult(level=level, status_message=status_message)
        )


AutomateFunction = Callable[[AutomationContext, T], None]
AutomateFunctionWithoutInputs = Callable[[AutomationContext], None]


@overload
def execute_automate_function(
    automate_function: AutomateFunction[T],
    input_schema: type[T],
) -> None:
    ...


@overload
def execute_automate_function(automate_function: AutomateFunctionWithoutInputs) -> None:
    ...


def execute_automate_function(
    automate_function: AutomateFunction[T] | AutomateFunctionWithoutInputs,
    input_schema: type[T] | None = None,
):
    """Runs the provided automate function with the input schema."""
    # first arg is the python file name, we do not need that
    args = sys.argv[1:]

    if len(args) < 2:
        raise ValueError("too few arguments specified need minimum 2")

    if len(args) > 4:
        raise ValueError("too many arguments specified, max supported is 4")

    # we rely on a command name convention to decide what to do.
    # this is here, so that the function authors do not see any of this
    command = args[0]

    if command == "generate_schema":
        path = Path(args[1])
        schema = json.dumps(
            input_schema.model_json_schema(by_alias=True) if input_schema else {}
        )
        path.write_text(schema)

    elif command == "run":
        automation_run_data = args[1]
        function_inputs = args[2]

        speckle_token = os.environ.get("SPECKLE_TOKEN", None)
        if not speckle_token and len(args) != 4:
            raise ValueError("Cannot get speckle token from arguments or environment")

        speckle_token = speckle_token if speckle_token else args[3]

        inputs = (
            input_schema.model_validate_json(function_inputs)
            if input_schema
            else input_schema
        )

        if inputs:
            automate_sdk = run_function(
                automate_function,  # type: ignore
                automation_run_data,
                speckle_token,
                inputs,
            )
        else:
            automate_sdk = run_function(
                automate_function,  # type: ignore
                automation_run_data,
                speckle_token,
            )

        exit_code = 0 if automate_sdk.run_status == AutomationStatus.SUCCEEDED else 1
        exit(exit_code)

    else:
        raise NotImplementedError(f"Command: '{command}' is not supported.")


@overload
def run_function(
    automate_function: AutomateFunction[T],
    automation_run_data: AutomationRunData | str,
    speckle_token: str,
    inputs: T,
) -> AutomationContext:
    ...


@overload
def run_function(
    automate_function: AutomateFunctionWithoutInputs,
    automation_run_data: AutomationRunData | str,
    speckle_token: str,
) -> AutomationContext:
    ...


def run_function(
    automate_function: AutomateFunction[T] | AutomateFunctionWithoutInputs,
    automation_run_data: AutomationRunData | str,
    speckle_token: str,
    inputs: T | None = None,
) -> AutomationContext:
    """Run the provided function with the automate sdk context."""
    automate_sdk = AutomationContext.initialize(automation_run_data, speckle_token)
    automate_sdk.report_run_status()

    try:
        # avoiding complex type gymnastics here on the internals.
        # the external type overloads make this correct
        if inputs:
            automate_function(automate_sdk, inputs)  # type: ignore
        else:
            automate_function(automate_sdk)  # type: ignore

        # the function author forgot to mark the function success
        if automate_sdk.run_status not in [
            AutomationStatus.FAILED,
            AutomationStatus.SUCCEEDED,
        ]:
            automate_sdk.mark_run_success(
                "WARNING: Automate assumed a success status,"
                " but it was not marked as so by the function."
            )
    except Exception:
        trace = traceback.format_exc()
        print(trace)
        automate_sdk.mark_run_failed(
            "Function error. Check the automation run logs for details."
        )
    finally:
        automate_sdk.report_run_status()
        return automate_sdk
