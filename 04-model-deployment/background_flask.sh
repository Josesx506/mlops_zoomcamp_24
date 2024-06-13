#!/bin/bash

# Check if the Flask server is already running
FLASK_PID=$(ps aux | grep '[p]ython local_flask/flask_predict.py' | awk '{print $2}')

if [ "$1" == "start" ]; then
    if [ -z "$FLASK_PID" ]; then
        echo "Starting Flask server..."
        nohup python local_flask/flask_predict.py > flask.log 2>&1 &
        echo "Flask server started."
    else
        echo "Flask server is already running with PID $FLASK_PID."
    fi
elif [ "$1" == "stop" ]; then
    if [ -n "$FLASK_PID" ]; then
        echo "Stopping Flask server with PID $FLASK_PID..."
        kill $FLASK_PID
        rm flask.log
        echo "Flask server stopped."
    else
        echo "Flask server is not running."
    fi
else
    echo "Usage: $0 {start|stop}"
fi