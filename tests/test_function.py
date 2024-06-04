"""Run integration tests with a speckle server."""

import os
import secrets
import string

from pydantic import SecretStr
from specklepy.logging.exceptions import SpeckleException

import pytest
from gql import gql
from speckle_automate import (
    AutomationContext,
    AutomationRunData,
    AutomationStatus,
    run_function,
)
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.objects.base import Base
from specklepy.transports.server import ServerTransport

from main import FunctionInputs, automate_function


def crypto_random_string(length: int) -> str:
    """Generate a semi crypto random string of a given length."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@pytest.fixture()
def speckle_token() -> str:
    """Provide a speckle token for the test suite."""
    env_var = "SPECKLE_TOKEN"
    token = os.getenv(env_var)
    if not token:
        raise ValueError(f"Cannot run tests without a {env_var} environment variable")
    return token


@pytest.fixture()
def speckle_server_url() -> str:
    """Provide a speckle server url for the test suite, default to localhost."""
    return os.getenv("SPECKLE_SERVER_URL", "http://127.0.0.1:3000")


@pytest.fixture()
def test_client(speckle_server_url: str, speckle_token: str) -> SpeckleClient:
    """Initialize a SpeckleClient for testing."""
    test_client = SpeckleClient(
        speckle_server_url, speckle_server_url.startswith("https")
    )
    test_client.authenticate_with_token(speckle_token)
    return test_client


@pytest.fixture()
def automation_run_data(
    test_client: SpeckleClient, speckle_server_url: str
) -> AutomationRunData:
    """Create automation run"""
    query = gql(
        """
        mutation CreateTestRun(
            $projectId: ID!,
            $automationId: ID!
        ) {
            projectMutations {
                automationMutations(projectId: $projectId) {
                    createTestAutomationRun(automationId: $automationId) {
                        automationRunId
                        functionRunId
                        triggers {
                            payload {
                                modelId
                                versionId
                            }
                            triggerType
                        }
                    }
                }
            }
        }
        """
    )

    params = {
        "automationId": os.getenv("SPECKLE_AUTOMATION_ID"),
        "projectId": os.getenv("SPECKLE_PROJECT_ID")
    }

    result = test_client.httpclient.execute(query, params)

    automation_run_data = result.get("projectMutations").get("automationMutations").get("createTestAutomationRun")
    trigger_data = automation_run_data.get("triggers")[0].get("payload")

    """Use result to create automation run data"""
    return AutomationRunData(
        project_id=os.getenv("SPECKLE_PROJECT_ID"),
        speckle_server_url=speckle_server_url,
        automation_id=os.getenv("SPECKLE_AUTOMATION_ID"),
        automation_run_id=automation_run_data.get("automationRunId"),
        function_run_id=automation_run_data.get("functionRunId"),
        triggers=[
            {
                "trigger_type": "versionCreation",
                "payload": {
                    "model_id": trigger_data.get("modelId"),
                    "version_id": trigger_data.get("versionId")
                }
            }
        ]
    )


def test_function_run(automation_run_data: AutomationRunData, speckle_token: str):
    """Run an integration test for the automate function."""
    automation_context = AutomationContext.initialize(
        automation_run_data, speckle_token
    )
    automate_sdk = run_function(
        automation_context,
        automate_function,
        FunctionInputs(
            forbidden_speckle_type="None",
            whisper_message=SecretStr("testing automatically"),
        ),
    )

    assert automate_sdk.run_status == AutomationStatus.SUCCEEDED
