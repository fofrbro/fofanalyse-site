# Service « École » de fofanalyse.com (espace de révision, du CM1 à la 6e).
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py ./
RUN rm -f test_*.py

# La progression vit dans /data (volume ecole_data), propriété de l'utilisateur du service.
RUN useradd --create-home --uid 10003 ecole && mkdir /data && chown ecole:ecole /data
USER ecole

EXPOSE 8000
CMD ["uvicorn", "app:creer_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
