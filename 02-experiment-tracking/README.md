### Assignment Scripts execution
1. MLFlow version
    ```python
    import mlflow
    print(mlflow.__version__)
    ```
2. Preprocess data
    ```python
    python 02-experiment-tracking/hw2/preprocess_data.py \
        --raw_data_path ./data/hw2/train --dest_path ./data/hw2/preprocessed
    ```
3. Train simple RFRegressor model with autolog. Modify the inputs to track my local uri and experiment name. Not specifying the experiment name allow it to log the experiment in the mlflow default experiment path.
    ```python
    python 02-experiment-tracking/hw2/train.py --data_path ./data/hw2/preprocessed
    ```
4. Add `default-artifact-root` to specify a local directory for saving artifacts when launching a local server.
5. Perform hyperparameter optimization with autolog disabled for the RFRegressor model. This creates a new experiment. Include the ml-flow tracker in only the objective function and log the *hyperparameters* and *validation rmse* only.
    ```python
    python 02-experiment-tracking/hw2/hpo.py --data_path ./data/hw2/preprocessed --num_trials 15
    ```
6. Automatically get the top 5 runs in the previous experiment based on the rmse and register it in the model registry. Modify the script to update the search runs criteria and the model name. 
    - ***Note***: The metric for sorting the best models in the final experiment should be `test_rmse` and not `rmse` because the automatic logging does not retain rmse.
    - If you make a mistake with an experiment like the rmse vs test_rmse and you push the wrong model, delete the experiment in the mlflow does not remove it from the backend. You would need to connect to your backend server and remove it manually. I followed the example in this [stack-overflow post](https://stackoverflow.com/questions/60088889/how-do-you-permanently-delete-an-experiment-in-mlflow), and automated a response that works with a postgres server using *psycopg2*. You can use pymysql to fix a mysql backend and rephrase the SQL commands where necessary. 
    ```python
    python 02-experiment-tracking/hw2/register_model.py --data_path ./data/hw2/preprocessed --top_n 5
    ```
7. Great assignment, I thoroughly enjoyed it and I look forward to the rest of the course. For now, it's back to Odin Project and node. Working towards the fullstack ml scientist.