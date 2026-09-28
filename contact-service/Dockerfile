# Service du formulaire de contact de fofanalyse.com.
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY contact.py .

RUN useradd --create-home --uid 10002 contact
USER contact

EXPOSE 8000
CMD ["uvicorn", "contact:app", "--host", "0.0.0.0", "--port", "8000"]
