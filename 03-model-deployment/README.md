### Orchestration
A data preprocessing and prediction pipeline is developed with `mage` in a separate repo. <br><br>

Environment variables can be setup within mage to hide keys like the column names being preprocessed for security purposes. The docker environment was setup with a postgres db within a docker container for the purpose of the tutorial. Launch the container with `.scripts/start.sh` from mlops folder. Access the UI from `http://localhost:6789` <br><br>

1. Create a data preparation ***`pipeline`***. It can have an `ingest`,`transform`, and `build` stages which are all just python scripts reading data from an api/db endpoint. Unit tests can also be included.
2. Create a ***global data product***. This accepts the output from the data preparation pipeline and allows you to access the exports as a variable in mage. The data product variable name can then be passed into a prediction pipeline. If the training set is already computed, it wont recompute it.
    - Multiple models can share the same global data product.
3. Create a dynamic custom python block to load the different model types to mage. This doesn't require a connection to the global data product.
    - Add helper functions for training the model and testing hyperparameters in the utils folder.
    - The output of each pipeline block is passed as input into the next pipeline.
4. Create a hyperparameter tuning transformer block to get the training data from step 2 and all the model types e.g. Linear and Lasso regression from step 3 as input. It then performs hyperparameter tuning on both models dynamically.
    - MLFlow experiment tracker can be passed as a callback to track and log the status of experiments during hyper-parameter tuning.
5. The final pipeline block takes the output parameters from the hyperparameter tuning, and trains the final model using the best parameters. This saves the model pickle files to memomry.

This step was repeated using two different pipelines for an sklearn and xgboost model respectively.