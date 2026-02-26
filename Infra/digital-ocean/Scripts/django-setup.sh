#!/bin/bash
 #upate system
    apt-get update && apt-get upgrade -y

    #installing Docker
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        fi

#Pull pre-built Django image from GitHub Container Registry
docker pull ghcr.io/ALIBCJH/digital-transformation-backend:latest

docker run -d --name django-backend \
    --restart=unless-stopped  \
    -p 8000:8000  \
    -e SECRET_KEY="${django_secret_key}" \
    -e ALLOWED_HOSTS="${allowed_hosts},localhost,127.0.0.1" \
    -e DATABASE_URL="postgres://${db_user}:${db_password}@${db_host}:${db_port}/${db_name}" \
    -e DB_NAME="${db_name}" \
    -e DB_USER="${db_user}" \
    -e DB_PASSWORD="${db_password}" \
    -e DB_HOST="${db_host}" \
    -e DB_PORT="${db_port}" \
    -e CORS_ALLOWED_ORIGINS="http://${frontend_ip}" \
    ghcr.io/ALIBCJH/digital-transformation-backend:latest

#Run Database MIgrations
sleep 10
docker exec  django-backend python manage.py migrate
docker exec django-backend python manage.py collectstatic --noinput