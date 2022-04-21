FROM python:3.9.2
RUN pip install --upgrade pip

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE = 1 \
    # Turns off buffering for easier container logging
    PYTHONUNBUFFERED = 1

COPY ./microservices/ms-omero-sessions /app/services/app
COPY ./common /app/common

WORKDIR /app/services/app

RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile && pip install flask-restx==0.5

EXPOSE 8080
CMD ["python", "app.py"]
