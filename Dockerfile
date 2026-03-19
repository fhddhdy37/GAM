FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# (권장) 빌드에 필요한 최소 패키지 (필요 없으면 제거)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl \
#   && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app