#!/usr/bin/env bash

docker build -f ./microservices/ms-omero-sessions/Dockerfile -t spex.omero.sessions:latest .
docker tag spex.omero.sessions:latest ghcr.io/genentech/spex.omero.sessions:latest
docker push ghcr.io/genentech/spex.omero.sessions:latest