### Environment Setup
Install virtual environment with pipenv `pipenv install numpy==1.26.4 flask --python=3.12`. Additional environment packages are in the `requirements.txt` and `Pipfile` files. <br>

Create a docker-compose setup for grafana. The compose file should have central mounted volume for storing data.
- Create a `config` directory for storing the grafana configuration yaml files. This allows a configuration of the postresql db to point to grafana dashboard. The environment is run locally and all services are free but you have to uses `http://localhost/<app_port>` to access the correct service like grafana.
- Default grafana username and password is `admin` and `admin`, following which you are prompted to set a new password.


### Evidently Monitoring and Dashboard
Evidently allows us to calculate metrics like ***`drift`*** given a base (training) and reference (val/test) dataset. The results can be queried programmatically or viewed from a dashboard. Typically, dashboards are associated with reports which are saved within project workspaces. A typical workflow is:
- Create a **workspace**
- Create a ***new project*** within the workflow
    - Save the project
- Create a new *Report* within the project
    - Add the project's report to the workspace
- Configure a *Dashboard* to visualize the project data
- Visualize the workspace either using 
    - `evidently ui` from terminal. Don't forget to active the pipenv virtual environment with `pipenv shell` before launching the ui
    - directly within a jupyter nb.
When you login to the UI, the configured dashboards, reports, and any test sessions can be viewed as individual tabs or downloaded. <br><br>
- ***Note***: When creating a report, a timestamp value (daily resolution) has to be included, The data passed to the report object should be limited to that day unless, it will associate multiple days of data to the specified timestamp.

The data from the report is referred to as `current` when creating the dashboard, and the metrics can be viewed programmatically with `regular_report.as_dict()`. <br><br>
The evidently report can be updated as a batch job using a cron schedule with prefect, mage, or github actions.

### Monitoring Tests
Tests for data and prediction drift can be implemented. 
- E.g. for data, we expect the training and predicted data to have similar distributions if we want the model to perform well. 
    - By measuring the drift distance using methods like the `normalized Wassertein Distance` and histograms we can visualize how the distributions change.
- For models, we can also measure metrics like accuracy or distance based drift methods to figure out when to retrain the models.
- The tests can be performed using evidently `TestSuite()` or `Report()` objects and the results are best output as dictionaries. This way, we can programmatically extract drift ways and include automatic retrain triggers.
- Tests like this also provide explanations for why model performance can decrease or increase. 



### Grafana Dashboard
- Create a dummy test postgres db and table.
- Make sure your `config/grafana_datasources.yaml` is properly configured to match your docker-compose files so that grafana knows which dashboard to extract data from.
- Execute the `dummy_metrics.py` script to create the dummy dataset, insert entries into the db with a time delay,this way, you can see the data coming in periodically into the Grafana dashboard.
    - **Note** - Using SQLAlchemy and grafana simulataneously causes sqlalchemy and the grafana admin users to clash, so it is better to connect with pyscopg directly.
- If the UI query selector in grafana doesn't detect your table, use the code query selector instead with `SELECT * FROM dummy_metrics LIMIT 50;`. This is what helped me visualize my dashboard
- Don't forget to save the dashboard panel once you're done.
- Dashboard schemas can be defined programmatically as `json` schemas and saved in the `./dashboards` directory, which will be passed into docker when creating the images.
- If the dashboard doesn't *`auto-refresh`* automatically, you can always toggle it on for specified durations.
- Although the data we were reading was from a saved dataframe, in a live scenario, I'll expect to read the data from a db
    - Read the data from 2 dbs, the first table shows observed outages, while the second table shows predicted outages. The drift from both tables can then be mapped as evidently columns and used to create a report. ***Prediction drift*** can be monitored from the report with Grafana, and alerts can be triggered when the performance drops below  a threshold.
- The scripts can also be passed into prefect workflows for orchestration purposes.