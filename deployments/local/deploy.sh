#!/bin/bash
SSH_HOST=$1
AWS_ACCESS_KEY=$2
AWS_SECRET_KEY=$3
REPO="590183744678.dkr.ecr.us-east-2.amazonaws.com"
IMG_NAME="energy-bills:latest"

aws configure set aws_access_key_id $AWS_ACCESS_KEY
aws configure set aws_secret_access_key $AWS_SECRET_KEY
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin $REPO
deployments/local/build.sh
docker tag $IMG_NAME "$REPO/$IMG_NAME"
docker push "$REPO/$IMG_NAME"
ssh $SSH_HOST "./pull.sh && exit" # Needs to have host configured in ~/.ssh/config
