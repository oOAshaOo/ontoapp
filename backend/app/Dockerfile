# pull official base image in 3.13.0
FROM python:3.13.0-alpine

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /

CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "1", "app:create_app()"]
