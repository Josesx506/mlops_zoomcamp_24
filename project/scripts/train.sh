# Activate the poetry virtual environment
cd backend/

# Start a mlflow server
poetry run mlflow server -h 0.0.0.0 -p 5150 --backend-store-uri=sqlite:///mlflow.db &

# Run the training pipeline
poetry run python pkg/model/train.py

# Start the simulated monitoring pipeline. 
# This requires docker because of grafana and postgres
# poetry run python pkg/model/sim_monitor.py &

# Start the gunicorn server
poetry run gunicorn --bind 0.0.0.0:8534 pkg.app.server:app &

# Find the gunicorn process ids and kill them e.g
# pgrep -fl gunicorn
# kill 11894
# If you don't have any other gunicorn servers running pgrep again
# will return an empty response