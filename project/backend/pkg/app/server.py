from flask import Flask, jsonify, request
from datetime import datetime
from pkg.app.load_model import load_trained_model


model = load_trained_model("s3")
app = Flask("motor_incident_predictions")


def prepare_features(query):
    loc_id = int(query["location_id"])
    dy = int(query["dowk"])
    hr = int(query["hour"])
    features = {"location_id": loc_id, "dowk": dy, "hour": hr}
    return features

def predict(features):
    preds = model.predict(features)
    return preds


@app.route("/predict_collisions", methods=["POST"])
def get_vehicle_collisions():
    query = request.get_json()
    features = prepare_features(query)
    n_incidents = predict(features)[0]

    result = {
        "incidents": f"{n_incidents:.2f}"
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port = 8534)