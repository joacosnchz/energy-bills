#!/bin/bash
docker run --rm --env-file .env -e JOB=$1 -t 590183744678.dkr.ecr.us-east-2.amazonaws.com/energy-bills:latest >> "logs/energy-bills.$(date +'%Y-%m-%d').log"
