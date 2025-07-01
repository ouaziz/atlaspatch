FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN python manage.py collectstatic --noinput --clear || true
EXPOSE 8000
CMD ["gunicorn", "atlaspatchserver.wsgi:application", "--bind", "0.0.0.0:8000"]