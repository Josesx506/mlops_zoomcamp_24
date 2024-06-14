import pickle
import mlflow
from flask import Flask, request, jsonify

tracking_uri = "http://ec2-100-26-136-60.compute-1.amazonaws.com:5000"
RUN_ID = "463c2a7966b84dd5b84b0ad3ca7c64ba"
S3_BUCKET = "mlflow-artifacts-joses"

def load_model(mlflow_uri,s3_bucket,run_id):
    mlflow.set_tracking_uri(mlflow_uri)
    model_uri = f"s3://{s3_bucket}/1/{run_id}/artifacts/model"
    loaded_model = mlflow.pyfunc.load_model(model_uri)
    return loaded_model

model = load_model(tracking_uri,S3_BUCKET, RUN_ID)


app = Flask("duration_prediction")

def prepare_features(ride):
    features = {}
    PU,DO = ride["PULocationID"], ride["DOLocationID"]
    features["PU_DO"] = f"{PU}_{DO}"
    features["trip_distance"] = ride["trip_distance"]
    return features

def predict(features):
    preds = model.predict(features)
    return preds[0]

@app.route("/predict", methods=["POST"])
def get_ride_duration():
    ride = request.get_json()
    features = prepare_features(ride)
    pred = predict(features)

    result = {"duration": f"{pred:.4f} minutes"}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port = 2024)