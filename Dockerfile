# Stage 1: Build stage
FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1

# Set the working directory in the container
WORKDIR /builder

COPY /requirements.txt ./

# Install dependencies including uvicorn
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 2: runtime
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1

WORKDIR /PostManagementAPI

# Copy dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /builder /PostManagementAPI
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

COPY wait-for-it.sh ./
COPY docker-entrypoint.sh ./

RUN chmod +x wait-for-it.sh
RUN chmod +x docker-entrypoint.sh

# Command to run server
ENTRYPOINT ["./docker-entrypoint.sh"]