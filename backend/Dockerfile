FROM docker:cli AS docker-cli

FROM python:3.13-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY --from=docker-cli /usr/local/bin/docker /usr/local/bin/docker

COPY backend backend

RUN useradd -m appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
