#!/bin/bash
aws configure set aws_access_key_id $AWS_ACCESS_KEY
aws configure set aws_secret_access_key $AWS_SECRET_KEY
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 590183744678.dkr.ecr.us-east-2.amazonaws.com
deployments/local/build.sh
docker tag energy-bills:latest 590183744678.dkr.ecr.us-east-2.amazonaws.com/energy-bills:latest
docker push 590183744678.dkr.ecr.us-east-2.amazonaws.com/energy-bills:latest
