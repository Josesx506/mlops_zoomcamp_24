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
The evidently report can be updated as a batch job using a cron schedule.


### Grafana Dashboard