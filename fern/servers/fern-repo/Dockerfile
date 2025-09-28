FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install mcp gitpython pytest

CMD ["python", "server.py"]
