FROM python:3.10.13-slim

COPY [ "Pipfile", "Pipfile.lock", "scoring.py", "test.py", "/app/"]

WORKDIR "/app"

RUN pip install -U pip

RUN pip install pipenv

RUN pipenv install --system --deploy

ARG AWS_KEY
ARG AWS_SECRET_KEY
ARG AWS_REGION

RUN aws configure set aws_access_key_id $AWS_KEY \
&& aws configure set aws_secret_access_key $AWS_SECRET_KEY \
&& aws configure set default.region $AWS_REGION

EXPOSE 2024

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:2024", "scoring:app" ]