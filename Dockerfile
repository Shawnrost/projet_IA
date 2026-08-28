FROM python:3.11-slim

# Empêche Python de bufferiser les logs (utile pour voir les logs sur HF Spaces)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code du projet
COPY . .

# Récupération du modèle versionné par DVC (si un remote DVC est configuré)
# Décommente si tu configures un accès au remote DVC pendant le build :
# RUN dvc pull model_output/model.pkl.dvc

# Migrations Django (si besoin d'une base de données locale, ex: SQLite)
WORKDIR /app/api
RUN python manage.py migrate --noinput

# Render fournit dynamiquement le port via la variable d'environnement $PORT
EXPOSE 8000

# Lancement en production avec Gunicorn (pas runserver)
# shell form du CMD pour que $PORT soit bien interprété au démarrage du conteneur
CMD gunicorn churn_api.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2