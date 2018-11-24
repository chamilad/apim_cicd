#!/usr/bin/env bash

set -e

command -v docker-compose >/dev/null 2>&1 || {
    echo >&2 "Docker Compose cannot be found. Aborting..."
    exit 1
}

echo "Validating..."
docker-compose config -q

echo "Starting two Docker Containers for WSO2 API Manager..."
docker-compose up --detach --no-recreate
docker-compose ps

echo
echo "IP Addresses:"
echo "=============="
docker ps --filter "name=api-manager" | awk '{if(NR>1)print $1}' | xargs docker inspect --format='{{.Name}}: {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' | sed -e 's/\///'
