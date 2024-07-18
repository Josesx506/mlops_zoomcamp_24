# Start a docker container to simulate AWS services with localstack
docker run --rm -d --name localstack_test_cntr -p 4569:4566 -e "SERVICES=s3" localstack/localstack
docker run --rm -d --name mlflow_test -p 5300:5000 ghcr.io/mlflow/mlflow mlflow server --host 0.0.0.0

# Create an environment variable for the python files
export S3_ENDPOINT_URL="http://localhost:4569/"
export S3_BUCKET_NAME="s3://nyc-collisions"
export MODEL_REGISTRY_URI="http://localhost:5300"
export EXPERIMENT_NAME="nyc-model-tests"

# sleep to allow the container spin up
sleep 10

# Create an s3 bucket in the localstack environment
aws s3 mb ${S3_BUCKET_NAME} --endpoint-url=http://localhost:4569/

# Populate the s3 bucket with files in the data folder
aws s3 cp ./data/saved_artifact ${S3_BUCKET_NAME} --recursive --endpoint-url=http://localhost:4569/
aws s3 cp ./data/NYCTaxiZones.geojson ${S3_BUCKET_NAME} --endpoint-url=http://localhost:4569/

# Check the bucket contents for interactive testing purposes
aws s3 ls ${S3_BUCKET_NAME} --recursive --endpoint-url=http://localhost:4569/

# Run the tests.
rm ./data/last_accessed.json
cd backend/

# Environment has already been installed in `make setup`
# poetry install
poetry run pytest

# Catch any errors
ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker stop localstack_test_cntr
    docker stop mlflow_test
    exit ${ERROR_CODE}
fi

# Shut down the container
docker stop localstack_test_cntr
docker stop mlflow_test