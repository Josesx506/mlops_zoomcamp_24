FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim

COPY [ "Pipfile", "Pipfile.lock", "score.py", "./"]

RUN pip install -U pip

RUN pip install pipenv

RUN pipenv install --system --deploy

CMD [ "python", "score.py", "yellow", "2023", "5" ]