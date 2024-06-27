### Unit tests
Test individual functions

### Integration tests
Test entire pipelines e.g writing to db and all endpoints with docker and bash scripting

`pipenv run pytest <test_dir>/` or `pytest <test_dir>/`


### LocalStack
[LocalStack](https://github.com/localstack/localstack) is an emulator to test AWS services locally. In this case, we"re simulating a kinesis stream. If you check existing streams with `aws kinesis list-streams`, it"ll be empty but you can simulate an AWS steam. 
1. Navigate to the `localstack` directory.
2. Export the environment variables and spin up the localstack kinesis instance from docker-compose.
    ```bash
    # Export environment variables that will be referenced in docker-compose
    export LOCAL_IMAGE_NAME=123
    export PREDICTIONS_STREAM_NAME=ride_predictions
    docker-compose up kinesis -d
    ```
3. Create a new stream named `ride_predictions` in localstack with 
    ```bash
    aws --endpoint-url=http://localhost:4568/ kinesis create-stream \
        --stream-name ride_predictions \
        --shard-count 1
    ```
4. View existing localstack streams with `aws --endpoint-url=http://localhost:4568/ kinesis list-streams`
5. Include the name of the aws service pointing to localstack in the docker-compose file `- KINESIS_ENDPOINT_URL=http://kinesis:4568/`
6. With bash and localStack, we can create integration tests to write to AWS kinesis stream and simulate how the data is read by our systems.

#### Read data from the Stream
1. Specify a shard id as the first shard since we created only 1
2. After running the test and inserting a message into the stream, read the shard iterator.
3. Extract the json as a base64 encoded message into the `${RESULT}` variable.
4. Decode the message.

    ```bash
    export SHARD="shardId-000000000000"

    SHARD_ITERATOR=$(aws --endpoint-url=http://localhost:4568/ kinesis \
        get-shard-iterator \
            --shard-id ${SHARD} \
            --shard-iterator-type TRIM_HORIZON \
            --stream-name ${PREDICTIONS_STREAM_NAME} \
            --query "ShardIterator" \
    )

    RESULT=$(aws --endpoint-url=http://localhost:4568/ \
        kinesis get-records --shard-iterator $SHARD_ITERATOR)

    echo ${RESULT} | jq -r ".Records[0].Data" | base64 --decode
    ```

#### Using localstack with boto3 in a python script
If the kinesis stream is working in docker, the endpoint environment variable can be used in a python script.
```python
kinesis_endpoint = os.getenv("KINESIS_ENDPOINT_URL", "http://localhost:4568/")
kinesis_client = boto3.client("kinesis", endpoint_url=kinesis_endpoint)
s3_client = boto3.client("s3", endpoint_url=kinesis_endpoint)
```
Other examples like setting up a [mock-s3 bucket](https://docs.localstack.cloud/user-guide/aws/s3/) is shown here