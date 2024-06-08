### Orchestration
A data preprocessing and prediction pipeline is developed with `mage` in a separate repo. <br><br>

### Training and Logging
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

This step was repeated using two different pipelines for an `sklearn` and `xgboost` model respectively.


### Observability
Dashboards can be created for each pipeline to visualize trigger types and successful pipeline runs. Each dashboard is fully customizable and the charts can be resized dynamically. Check out these videos([video1](https://www.youtube.com/watch?v=jwte-x3VwFE&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=34),[video2](https://www.youtube.com/watch?v=Skr-WnxiQ8I&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=34)) for additional help. <br><br>

For the xgboost pipeline, an additional custom data pipeline block was included to generate the data to be used for the dashboard. <br>
**Note**: All the outputs in the pipeline have to be run manually before the plot loads. Executing the pipeline without running each cell gave me plotting errors. <br><br>

Additional dashboards were created to visualize performance of all the models simultaneously. I encountered an error ***`Cannot cast DatetimeArray to dtype float64`*** while trying to replicate the dashboard. I had to modify to custom plotting script as shown below to make it work.
```python
from mlops.utils.analytics.data import load_data
import numpy as np
# https://docs.mage.ai/visualizations/dashboards

@data_source
def data(*args, **kwargs):
    df=load_data()
    df['start_time']=df['start_time'].astype(np.int64)//10**9
    return df
```

Email alerts can be triggered when a pipeline is completed or when a pipeline fails.

### Retraining
Models can be retrained using a pipeline that triggers other pipelines like the sklearn and xgboost training pipelines trained in part two. The retrain pipeline can be configured to skip if its currently active or ignore failed execution blocks. The trigger can be deployed to work on a schedule like [here](https://www.youtube.com/watch?v=6kcBWl3E8So&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=44).

### Predictions
Predictions can be setup as pipeline in Mage although this is not too efficient. Setting up a backend server is more efficient. In mage, you can pass in a series of manual input queries and pass the predictions into a pipeline or package the inputs as a json request. <br><br>

The trained model pipeline can be registered as a global data product and passed to the custom inference python script for prediction results. The pipeline would contain the preprocessing vectorizer and trained model objects. The prediction pipeline can then be triggered via an api to obtain results.
```bash
curl -X POST http://localhost:6789/api/pipeline_schedules/3/pipeline_runs/abc123 \
  --header 'Content-Type: application/json' \
  --data '
{
  "pipeline_run": {
    "variables": {
      "env": "staging",
      "schema": "public"
    }
  }
}'
```
Additional details can be found [here](https://www.youtube.com/watch?v=mytcFbH_ooY&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=47) and [here](https://www.youtube.com/watch?v=J6ckSZczk8M&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=49ß).<br><br>

A basic UI can be setup on top of a mage pipeline block as an [interaction](https://www.youtube.com/watch?v=JI0dhR7Bnhk&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=47).