# mlops_joses
mlops_classes

Launch MLFlow UI with `mlflow ui`. I install postgres locally on my laptop and used a local postgres db. I needed to install *psycopg2* for psql. It can also be swapped with AWS RDS from the env file.
- **Bugs**
    - If you encounter an ***Access denied error*** in Chrome, navigate to `chrome://net-internals/#sockets` and flush socket pools to regain access. This is a problem from the flask server.
    - If you encounter any bugs with psql restarting after disconnecting, restart pqsl with brew `brew services restart postgresql@14` or delete the *.pid* file `rm /usr/local/var/postgresql\@14/postmaster.pid` and restart the postgres server. Don't forget to change your version number if you're using something different.
- Postgres SQL format is `postgresql://{DB_USER}:{DB_PASSWORD}@localhost:{PORT}/{database_name}`. My db name was *mlops*.
- Connect it the mlfow UI with `mlflow ui --backend-store-uri postgresql://josesmac:@localhost:5432/mlops --default-artifact-root mlflow-experiments`. Where `mlflow-experiments` is a local folder. The artifact root can also be replaced with an s3 bucket like `s3://S3_BUCKET_NAME`.
- You can also use sqlite for local tests easily with `mlflow ui --backend-store-uri sqlite://mlflow.db`

Trained models that have been logged to a remove registry and artifact bucket remotely can be accessed using the model uri.

#### Caching
Caching allows storage of data into local memory. User keys can be used to uniquely differentiate global vs user specific data in cache. The keys should be hashed for security purposes.
Cache Memoization allows caching of a function as well as its input arguments, so that the function is only recomputed whenever the arguments change.

#### Learning
- [ ] Orchestration and retraining pipelines
- [ ] Statistical distribution of reference and current data (Data Drift)
- [ ] Model Prediction Drift
- [ ] Docker-compose for provisioning resources
- [ ] Mocking in pytests
    - AWS mocking with localStack

- Bash commands to 
    - cd to the directory of the script is `cd "$(dirname "$0")"`
    - Date Fomat in bash `date +"%Y-%m-%dT%H:%M:%S"`
    - Exit upon first interrupt encountered `set -e`
