#!/usr/bin/env bash

set -e

command -v docker-compose >/dev/null 2>&1 || {
    echo >&2 "Docker Compose cannot be found. Aborting..."
    exit 1
}

docker-compose down --remove-orphans
