FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/api
RUN python manage.py migrate --noinput

EXPOSE 7860

CMD ["gunicorn", "churn_api.wsgi:application", "--bind", "0.0.0.0:7860", "--workers", "2"]