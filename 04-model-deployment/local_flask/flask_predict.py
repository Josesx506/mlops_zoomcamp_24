import pickle
from flask import Flask, request, jsonify

try:
    with open("models/lin_reg.bin", "rb") as f_in:
        (dv, model) = pickle.load(f_in)
except:
    with open("../models/lin_reg.bin", "rb") as f_in:
        (dv, model) = pickle.load(f_in)

app = Flask("duration_prediction")

def prepare_features(ride):
    features = {}
    PU,DO = ride["PULocationID"], ride["DOLocationID"]
    features["PU_DO"] = f"{PU}_{DO}"
    features["trip_distance"] = ride["trip_distance"]
    return features

def predict(features):
    X = dv.transform(features)
    preds = model.predict(X)
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