FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install fastapi uvicorn pytest

EXPOSE 8000
CMD ["python", "server.py"]
