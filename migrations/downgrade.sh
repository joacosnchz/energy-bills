#!/bin/bash
./build.sh
docker run --rm -t --network host --env-file .env energy-bills-migrations downgrade -1
