# Base stage
FROM python:3.9-slim AS base

WORKDIR /app

# Install git and dependencies
RUN apt-get update && apt-get install -y git
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# API stage
FROM base AS api

# Worker stage
FROM base AS worker

# Clone the android_rinex repository
RUN rm -rf /app/android_rinex && git clone https://github.com/rokubun/android_rinex.git

# Make the gnsslogger_to_rnx script executable
RUN chmod +x /app/android_rinex/bin/gnsslogger_to_rnx