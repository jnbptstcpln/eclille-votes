# Image figée sur Debian bookworm (python:3.9-slim pointe maintenant sur trixie)
FROM python:3.9-slim-bookworm

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# gcc + libmysqlclient pour mysqlclient, curl pour le healthcheck Coolify,
# libjpeg/zlib au cas où Pillow doive être compilé
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    default-libmysqlclient-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=cla_votes.settings.coolify
RUN chmod +x /usr/src/app/entrypoint.sh
EXPOSE 8000
CMD ["/usr/src/app/entrypoint.sh"]
