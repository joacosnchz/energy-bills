#!/bin/bash
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 590183744678.dkr.ecr.us-east-2.amazonaws.com
docker pull 590183744678.dkr.ecr.us-east-2.amazonaws.com/energy-bills:latest
