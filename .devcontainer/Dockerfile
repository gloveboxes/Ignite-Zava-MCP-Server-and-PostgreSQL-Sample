FROM mcr.microsoft.com/devcontainers/python:3.13-bookworm

# Install pip for Python 3.13
RUN python -m pip install --upgrade pip

# Install PostgreSQL client tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg lsb-release wget \
    && sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg \
    && apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client-17 \
    && rm -rf /var/lib/apt/lists/*

# Install DevTunnel CLI
# RUN curl -sL https://aka.ms/DevTunnelCliInstall | bash && \
#     cp /root/bin/devtunnel /usr/local/bin/devtunnel

# # Install Aspire CLI
# RUN curl -sSL https://aspire.dev/install.sh | bash && \
#     cp /root/.aspire/bin/* /usr/local/bin/ 2>/dev/null || true

# Install the packages required to run the workshop as a student
COPY requirements.lock.txt .
RUN pip install -r requirements.lock.txt
