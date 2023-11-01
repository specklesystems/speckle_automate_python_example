# We use the official Python 3.11 image as our base image and will add our code to it. For more details, see https://hub.docker.com/_/python
FROM python:3.11-slim

# Speckle Automate will run the container as a non-root user, which we will name 'speckle'.
# The following creates a group named 'speckle' with an id of 1000, and a user named 'speckle' with an id of 65534. The speckle user is part of the speckle group.
# The `-m` flag creates a home directory for the user, which is required by the SpecklePy SDK; a config file will be saved here at /home/speckle/.config
#
# If running the image locally, e.g. for testing, you should also run it as a non-root user using the `--user speckle:speckle` flag
# e.g. docker run --rm -it --user speckle:speckle speckle_automate_python_example
# You can verify the user by running `import getpass; print(getpass.getuser())` in the python shell; it should print 'speckle'
RUN groupadd --gid 1000 speckle && useradd -m --uid 60000 -g speckle speckle

# We install poetry to generate a list of dependencies which will be required by our application
RUN pip install poetry

# We set the working directory to be the root directory; all of our files will be copied here.
WORKDIR /home/speckle

# Copy all of our code and assets from the local directory into the /home/speckle directory of the container.
# We also ensure that the user 'speckle' owns these files, so it can access them
# This assumes that the Dockerfile is in the same directory as the rest of the code
COPY --chown=speckle:speckle . /home/speckle

# Using poetry, we generate a list of requirements, save them to requirements.txt, and then use pip to install them
RUN poetry export --format requirements.txt --output /home/speckle/requirements.txt && pip install --requirement /home/speckle/requirements.txt
