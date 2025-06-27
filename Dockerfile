# Stage 1: Build stage
FROM python:3.13-alpine3.21 AS build

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . .

# Stage 2: Runtime stage
FROM python:3.13-alpine3.21

WORKDIR /app

# Copy installed dependencies from the build stage
COPY --from=build /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

ARG UID
ARG GID

# Create a non-root user
RUN addgroup -S appuser -g $GID \
    && adduser -S appuser -u $UID -G appuser

USER appuser