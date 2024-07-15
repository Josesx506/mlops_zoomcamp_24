import mlflow
from pkg.app.app_utils import create_app
from pkg.model.data import load_shapefile
from pkg.model.utils import get_data_dir

"""
This script launches the server with one of the pretrained models
skipping the model training pipeline and evidently pipeline
"""
def load_local_model():
    model_uri = f"{get_data_dir()}/saved_artifact"
    model = mlflow.pyfunc.load_model(model_uri)
    return model

# Load the important data
model = load_local_model()
nyc_taxi_zones = load_shapefile()
app = create_app( model, nyc_taxi_zones)

if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port = 8536)
