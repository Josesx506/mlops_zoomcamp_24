from pkg.model.train import training_pipeline
from pkg.app.load_model import load_trained_model
from pkg.model.utils import remove_local_artifacts


def test_training_pipeline():
    train_dt:dict={"start":"2023-01-01","end":"2023-01-10"}
    test_dt:dict={"start":"2023-03-01","end":"2023-03-05"}
    pipe = training_pipeline(train_dt,test_dt, hyperparameter_tuning=False)
    assert pipe is None

def test_predictions():
    model = load_trained_model()
    assert model is not None

    test_query = {"location_id": 200, "dowk":5, "hour":20}
    pred = model.predict(test_query)

    assert pred is not None

    remove_local_artifacts()