#!/bin/bash
export PYTHONPATH=$PYTHONPATH:/app

# mlflow server -h 0.0.0.0 -p 5150 --backend-store-uri=postgresql://postgres:zmcp24@db:5432/mlflowdb --default-artifact-root=${S3_URI} &

# Run the training script
python pkg/model/train.py

# Run the scoring and monitoring script
python pkg/model/sim_monitor.py &      # Run in the background

# Run the Gunicorn server for predictions
exec gunicorn --bind 0.0.0.0:8534 pkg.app.server:app
