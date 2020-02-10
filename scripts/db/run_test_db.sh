#!/bin/bash
docker run -d --rm \
  --name pg-test \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=db \
  --network host \
  -v "$ROOT_PATH"/data/pgdata:/var/lib/postgresql/data \
  postgres