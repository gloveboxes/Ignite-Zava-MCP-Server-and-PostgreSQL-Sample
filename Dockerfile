FROM python:3.11-slim-bookworm

# Install system dependencies and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements file first for better layer caching
COPY requirements.lock.txt .

# Install Python dependencies and Azure CLI, then clean up pip cache and test files
RUN pip install --no-cache-dir -r requirements.lock.txt \
    && pip install --no-cache-dir azure-cli \
    && az --version \
    # Remove pip cache, test and dist-info files to reduce image size
    && rm -rf /root/.cache/pip \
    && find /usr/local/lib/python3.11/site-packages -type d -name "tests" -exec rm -rf {} + \
    && find /usr/local/lib/python3.11/site-packages -type d -name "__pycache__" -exec rm -rf {} +

# Copy only necessary app code
COPY mcp_server/ /app/mcp_server/

EXPOSE 8000
ENV PORT=8000 \
    AZURE_EXTENSION_USE_DYNAMIC_INSTALL=yes_without_prompt

# Add a health check to periodically verify the container's health
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python -m mcp_server.health_check || exit 1

CMD ["python", "-m", "mcp_server.sales_analysis"]