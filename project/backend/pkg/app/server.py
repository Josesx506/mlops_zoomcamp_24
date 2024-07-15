from pkg.app.load_model import load_trained_model
from pkg.app.app_utils import create_app
from pkg.model.data import load_shapefile


"""
Dynamic server connected to mlflow registry, spins up after
model training and evidently monitoring. Server hosts the best
performant model based on rms error
"""

model = load_trained_model("s3")
nyc_taxi_zones = load_shapefile()
app = create_app( model, nyc_taxi_zones)

if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port = 8534)