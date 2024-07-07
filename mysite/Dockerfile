FROM python:3.11.9

COPY . /app

WORKDIR /app

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

RUN pip install -r requirements.txt


CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]