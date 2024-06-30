1. Put all the variables in `batch.py` apart from the `read_data()` function inside a `main()` function. Main should accept 2 arguments, year and month and execute the rest of the script.
    - You'll need to create a folder named `output` manually.
2. Install pytest as a dev dependency.
3. Create a folder named `tests` and create a `test_batch.py` file inside. Inside the test_batch file, create a function `prepare_data()` that essentially mimic `read_data()`. Pass in the specified data, column names, and categorical columns to create a preprocessed dataframe. Write a test to assert the length of the output dataframe.
4. Create a docker-compose file with a localstack s3 service
    ``` bash
    services:
    s3:
        image: localstack/localstack
        restart: always
        ports:
        - "4569:4566"
        environment:
        - SERVICES=s3
    ```
    Create an s3 bucket within local stack using the make bucket command `aws s3 mb s3://nyc-duration --endpoint-url=http://localhost:4569/`. You can view the new bucket with `aws s3 ls --endpoint-url=http://localhost:4569/`, and it should return a timestamp and bucket name like
    > 2024-06-30 00:11:01 nyc-duration
    - Specify input and output formats for the test as environment variables using
    ```bash
    export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
    export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"
    export S3_ENDPOINT_URL="http://localhost:4569/"
    ```
    Save the test data from **Q3** into the emulated s3 bucket with the `write_to_s3.py` file. You can also view the s3 bucket contents with aws cli using `aws s3 ls s3://nyc-duration --recursive --endpoint-url=http://localhost:4569/`. You can delete files with `aws s3 rm s3://nyc-duration/out/2022-01.parquet --endpoint-url=http://localhost:4569/`
5. Use the environment variables to read and write from the s3 bucket in `integration_test.py` file. A shell script can be written to test the function. *My answer didn't match or come close for the first time. The instructions for which files to use were very vague*