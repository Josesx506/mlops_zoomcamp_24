### Peer Review Evaluations
1. ***Svetlana Ulianova***
    - **Project link** <br> 
    https://github.com/svetavasileva/dog-breed-classifier
    - **Review comments** <br>
        This is a great attempt, and the code is well documented with several assumptions. It appears the mlflow server will be hosted locally and the trained model will be tracked and registered locally before copying the final model to AWS to serve predictions. The problem with this implementation is that the app cannot update the model if new data is provided and it will require manually pushing changes because there's no remote mlflow server. Hyperparameter tuning and a retraining pipeline are also not implemented so the model can't adapt it's performance for new data. This is understable considering the training data is fixed and no new data is coming in. <br>

        The deployed model instance couldn't be accessed. This might be due to AWS security group settings. Overall it's a great submission especially the IAC provisioning, and hopefully these comments help you improve to become a better MLOps engineer.
    - **Other comments** <br>
        Great submission and congratulations on completing the zoomcamp
2. ***Vibrant Torvalds***
    - **Project link** <br>
        https://github.com/FrancescaBellucci/mlops-zoomcamp/tree/main/final_project
    - **Review comments** <br>
        This is a great attempt and the code is reproducible. There are some potential issues with the implementation, the first being that the package versions in the requirements.txt file are not specified. This can cause dependency clashes if an attempt to reproduce the project is made after the packages have been updated. <br>

        The training workflow is great and the use of tracked hyperparameters is commendable. The multi-model approach of Isolation Forest (ISF) and XGBoost is also interesting however, it can be confusing to apply when the model is used to serve predictions. E.g. If the model is hosted on a web server, and a json request is received, you'll have to first check whether it's an outlier with the ISF model before predicting with the XGB model. <br>

        Considering the different dependencies, it'll be helpful to containerize the results with tools like docker. You can also build a webserver to host predictions but the number of input features required to make a prediction can become cumbersome. Other best practices like orchestration, monitoring and deployment can also be implemented for future projects. <br>

        Overall it's a great submission especially the model training and orchestration. Hopefully these comments help you improve to become a better MLOps engineer.
    - **Other comments** <br>
        Good submission and congratulations on completing the zoomcamp
3. ***Brave McLean***
    - **Project link** <br>
        https://github.com/ppatrzyk/rss-store
    - **Review comments** <br>
        Great submission and containerizing the application made it easier to test. An improvement can be made to the docker-compose.yml file to access the Dockerfiles in the /rssagent and /mlagent folders so that those images don't have to be built manually. That part was confusing for setup, and it'll make it easier to deploy the model. <br>

        Reproducing the code was hard. E.g. to insert the sample sql query, I had to navigate to the postgres container `psql -U postgres`, access the rss table `\c rss`, and then copy and paste the insert query. All of these could have been automated with a simple psycopg2 python script within the mlagent dockerfile. <br>

        Also manually accessing the mlagent and rssagent bash terminals to trigger the deployments with `prefect deploy --prefect-file /flows/prefect.yaml` is inefficient. If the sample sql query was automated above, then the deployment could have been triggered within the docker-compose.yml as a command. <br>

        For the model registry, registering every new model that is trained is not a good practice. Typically you'll want to evaluate the model performance using a metric before registering the best model. In your implementation, once you receive data into your feeed and train the model, you just overwrite the previous models' version. Using the registry and tracking models is a good practice but your implementation can be improved. <br>

        For the orchestration, it was scheduled to run every minute and it keeps restarting the mlserver. All the curl requests failed to return a response in terminal, and I don't know if it's printing out a response somewhere else or if it just fails. In the future, it'll be better to design your webapp server to customize what a typical response is, and handle any errors better. It'll also be better to delay the cron schedule to maybe every hour or every 15 minutes before restarting the mlserver. <br>

        I understand it's a relatively complex setup with all the moving parts but simplifying the setup makes it easier for future deployments and implementing CI/CD best practices. <br>
        
        Overall it's a great submission especially the model orchestration with prefect to handle the rss feed and serve predictions. Hopefully these comments help you improve to become a better MLOps engineer.

    - **Other comments** <br>
        Good submission and congratulations on completing the zoomcamp







