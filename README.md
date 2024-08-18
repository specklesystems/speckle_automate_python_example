# Speckle Automate function template - Python

This template repository is for a Speckle Automate function written in Python
using the [specklepy](https://pypi.org/project/specklepy/) SDK to interact with Speckle data.

This template contains the full scaffolding required to publish a function to the Automate environment.
It also has some sane defaults for development environment setups.

## Getting started

1. Use this template repository to create a new repository in your own / organization's profile.

Register the function 

### Add new dependencies

To add new Python package dependencies to the project, use the following:
`$ poetry add pandas`

### Change launch variables

Describe how the launch.json should be edited.

### Github Codespaces

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
    - [Python 3](https://www.python.org/downloads/)
    - [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
1. Run `poetry shell && poetry install` to install the required Python packages.

## Building and Testing

The code can be tested locally by running `poetry run pytest`.

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
