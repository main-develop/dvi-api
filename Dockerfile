FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/app.py

WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.app:app"]
