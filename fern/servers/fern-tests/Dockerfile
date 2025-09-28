FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install mcp pytest

EXPOSE 8000
CMD ["python", "server.py"]
