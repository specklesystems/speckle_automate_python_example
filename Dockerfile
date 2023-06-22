FROM python:3.11

# RUN pip install poetry

COPY . .
RUN pip install -r requirements.txt
# RUN poetry install --no-root --no-dev
