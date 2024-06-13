import pickle

with open("models/lin_reg.bin", "rb") as f_in:
    (dv, model) = pickle.load(f_in)


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
