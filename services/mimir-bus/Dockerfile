FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mimir_bus ./mimir_bus

ENV MIMIR_HTTP_HOST=0.0.0.0
ENV MIMIR_HTTP_PORT=8090
ENV MIMIR_MQTT_BROKER=mqtt:1883
ENV MIMIR_DATA=/app/data

EXPOSE 8090
CMD ["python", "-m", "mimir_bus"]
