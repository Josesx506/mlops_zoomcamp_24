# mlops_joses
mlops_classes

Launch MLFlow UI with `mlflow ui`. I install postgres locally on my laptop and used a local postgres db. I needed to install *psycopg2* for psql. It can also be swapped with AWS RDS from the env file. 
- If you encounter an ***Access denied error*** in Chrome, navigate to `chrome://net-internals/#sockets` and flush socket pools to regain access. This is a problem from the flask server.
- Postgres SQL format is `postgresql://{DB_USER}:{DB_PASSWORD}@localhost:{PORT}/{database_name}`. My db name was *mlops*.
- Connect it the mlfow UI with `mlflow ui --backend-store-uri postgresql://josesmac:@localhost:5432/mlops --default-artifact-root mlflow-experiments`. Where `mlflow-experiments` is a local folder. The artifact root can also be replaced with an s3 bucket like `s3://S3_BUCKET_NAME`.
- You can also use sqlite for local tests easily with `mlflow ui --backend-store-uri sqlite://mlflow.db`

Trained models that have been logged to a remove registry and artifact bucket remotely can be accessed using the model uri.
