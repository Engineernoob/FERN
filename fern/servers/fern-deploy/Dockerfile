FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Install only MCP (no pytest/git needed here)
RUN pip install mcp

EXPOSE 8000
CMD ["python", "server.py"]
