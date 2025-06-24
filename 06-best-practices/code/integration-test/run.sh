#!/usr/bin/env bash

# cd the directory of the script
if [[ -z "${GITHUB_ACTIONS}" ]]; then
  cd "$(dirname "$0")" 
fi

# build docker image if not exists
if [ "${LOCAL_IMAGE_NAME}" == "" ]; then 
    LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
    export LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"
    echo "LOCAL_IMAGE_NAME is not set, building a new image with tag ${LOCAL_IMAGE_NAME}"
    docker build -t ${LOCAL_IMAGE_NAME} ..
else
    echo "no need to build image ${LOCAL_IMAGE_NAME}"
fi

export PREDICTIONS_STREAM_NAME="ride_predictions"

# run docker container
docker-compose up -d

sleep 5

# create kinesis stream using localstack
aws --endpoint-url=http://localhost:4566 \
    kinesis create-stream \
    --stream-name ${PREDICTIONS_STREAM_NAME} \
    --shard-count 1

# run test_docker.py
pipenv run python test_docker.py

ERROR_CODE=$? # exit code of the previous command, which is test_docker.py

# if test_docker.py failed, print the logs and stop the container
if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi


pipenv run python test_kinesis.py

ERROR_CODE=$? # exit code of the previous command, which is test_kinesis.py

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi


docker-compose down
