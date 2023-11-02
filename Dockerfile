# We use the official Python 3.11 image as our base image and will add our code to it. For more details, see https://hub.docker.com/_/python
FROM python:3.11-slim

# We install poetry to generate a list of dependencies which will be required by our application
RUN pip install poetry

# We set the working directory to be the /home/speckle directory; all of our files will be copied here.
WORKDIR /home/speckle

# Copy all of our code and assets from the local directory into the /home/speckle directory of the container.
# We also ensure that the user 'speckle' owns these files, so it can access them
# This assumes that the Dockerfile is in the same directory as the rest of the code
COPY . /home/speckle

# Using poetry, we generate a list of requirements, save them to requirements.txt, and then use pip to install them
RUN poetry export --format requirements.txt --output /home/speckle/requirements.txt && pip install --requirement /home/speckle/requirements.txt
