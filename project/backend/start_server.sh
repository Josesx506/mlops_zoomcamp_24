#!/bin/bash
export PYTHONPATH=$PYTHONPATH:/app

# Run the training script
python pkg/model/train.py

# Run the scoring and monitoring script
python pkg/model/sim_monitor.py &      # Run in the background

# Run the Gunicorn server for predictions
exec gunicorn --bind 0.0.0.0:8534 pkg.app.server:app
