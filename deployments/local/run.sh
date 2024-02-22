#!/bin/bash
deployments/local/build.sh
docker run --rm --network host --env-file deployments/local/.env -t energy-bills
