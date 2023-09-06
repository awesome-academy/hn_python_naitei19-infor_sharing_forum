FROM python:slim
RUN apt-get update && apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
EXPOSE 8000
