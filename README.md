# Speckle Automate function template - Python

This template repository is for a Speckle Automate function written in Python
using the [specklepy](https://pypi.org/project/specklepy/) SDK to interact with Speckle data.

This template contains the full scaffolding required to publish a function to the Automate environment.
It also has some sane defaults for development environment setups.

## Getting started

1. Use this template repository to create a new repository in your own / organization's profile.
1. Register the function

### Add new dependencies

To add new Python package dependencies to the project, edit the `pyproject.toml` file:

**For packages your function needs to run** (like pandas, requests, etc.):
```toml
dependencies = [
    "specklepy==3.0.0",
    "pandas==2.1.0",  # Add production dependencies here
]
```

**For development tools** (like testing or formatting tools):
```toml
[project.optional-dependencies]
dev = [
    "black==23.12.1",
    "pytest-mock==3.11.1",  # Add development dependencies here
    # ... other dev tools
]
```

**How to decide which section?**
- If your `main.py` (or other function logic) imports it → `dependencies`
- If it's just a tool to help you code → `[project.optional-dependencies].dev`

Example:
```python
# In your main.py
import pandas as pd  # ← This goes in dependencies
import specklepy     # ← This goes in dependencies

# You won't import these in main.py:
# pytest, black, mypy ← These go in [project.optional-dependencies].dev
```

### Change launch variables

Describe how the launch.json should be edited.

### GitHub Codespaces

Create a new repo from this template, and use the create new code.

### Using this Speckle Function

1. [Create](https://automate.speckle.dev/) a new Speckle Automation.
1. Select your Speckle Project and Speckle Model.
1. Select the deployed Speckle Function.
1. Enter a phrase to use in the comment.
1. Click `Create Automation`.

## Getting Started with Creating Your Own Speckle Function

1. [Register](https://automate.speckle.dev/) your Function with [Speckle Automate](https://automate.speckle.dev/) and select the Python template.
1. A new repository will be created in your GitHub account.
1. Make changes to your Function in `main.py`. See below for the Developer Requirements and instructions on how to test.
1. To create a new version of your Function, create a new [GitHub release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository) in your repository.

## Developer Requirements

1. Install the following:
    - [Python 3.11+](https://www.python.org/downloads/)
1. Run the following to set up your development environment:
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate

    pip install --upgrade pip
    pip install .[dev]
    ```

**What this installs:**
- All the packages your function needs to run (`dependencies`)
- Plus development tools like testing and code formatting (`[project.optional-dependencies].dev`)

**Why separate sections?**
- `dependencies`: Only what gets deployed with your function (lightweight)
- `dev` dependencies: Extra tools to help you write better code locally

## Building and Testing

The code can be tested locally by running `pytest`.

### Alternative dependency managers

This template uses the modern **PEP 621** standard in `pyproject.toml`, which works with all modern Python dependency managers:

#### Using Poetry
```bash
poetry install  # Automatically reads pyproject.toml
```

#### Using uv
```bash
uv sync  # Automatically reads pyproject.toml
```

#### Using pip-tools
```bash
pip-compile pyproject.toml  # Generate requirements.txt from pyproject.toml
pip install -r requirements.txt
```

#### Using pdm
```bash
pdm install  # Automatically reads pyproject.toml
```

**Advantage**: All tools read the same `pyproject.toml` file, so there's no need to keep multiple files in sync!

### Building and running the Docker Container Image

Running and testing your code on your machine is a great way to develop your Function; the following instructions are a bit more in-depth and only required if you are having issues with your Function in GitHub Actions or on Speckle Automate.

#### Building the Docker Container Image

The GitHub Action packages your code into the format required by Speckle Automate. This is done by building a Docker Image, which Speckle Automate runs. You can attempt to build the Docker Image locally to test the building process.

To build the Docker Container Image, you must have [Docker](https://docs.docker.com/get-docker/) installed.

Once you have Docker running on your local machine:

1. Open a terminal
1. Navigate to the directory in which you cloned this repository
1. Run the following command:

    ```bash
    docker build -f ./Dockerfile -t speckle_automate_python_example .
    ```

#### Running the Docker Container Image

Once the GitHub Action has built the image, it is sent to Speckle Automate. When Speckle Automate runs your Function as part of an Automation, it will run the Docker Container Image. You can test that your Docker Container Image runs correctly locally.

1. To then run the Docker Container Image, run the following command:

    ```bash
    docker run --rm speckle_automate_python_example \
    python -u main.py run \
    '{"projectId": "1234", "modelId": "1234", "branchName": "myBranch", "versionId": "1234", "speckleServerUrl": "https://speckle.xyz", "automationId": "1234", "automationRevisionId": "1234", "automationRunId": "1234", "functionId": "1234", "functionName": "my function", "functionLogo": "base64EncodedPng"}' \
    '{}' \
    yourSpeckleServerAuthenticationToken
    ```

Let's explain this in more detail:

`docker run—-rm speckle_automate_python_example` tells Docker to run the Docker Container Image we built earlier. `speckle_automate_python_example` is the name of the Docker Container Image. The `--rm` flag tells Docker to remove the container after it has finished running, freeing up space on your machine.

The line `python -u main.py run` is the command run inside the Docker Container Image. The rest of the command is the arguments passed to the command. The arguments are:

- `'{"projectId": "1234", "modelId": "1234", "branchName": "myBranch", "versionId": "1234", "speckleServerUrl": "https://speckle.xyz", "automationId": "1234", "automationRevisionId": "1234", "automationRunId": "1234", "functionId": "1234", "functionName": "my function", "functionLogo": "base64EncodedPng"}'` - the metadata that describes the automation and the function.
- `{}` - the input parameters for the function the Automation creator can set. Here, they are blank, but you can add your parameters to test your function.
- `yourSpeckleServerAuthenticationToken`—the authentication token for the Speckle Server that the Automation can connect to. This is required to interact with the Speckle Server, for example, to get data from the Model.

## Resources

- [Learn](https://speckle.guide/dev/python.html) more about SpecklePy and interacting with Speckle from Python.
