### Setting up MLFlow Server with pipenv only
- Install packages to launch the environment
    ```bash
    sudo apt-get update
    sudo apt install python3-pip
    sudo python3 -m pip install awscli --break-system-packages
    aws configure              # Include access key and secret
    sudo apt install pipenv
    sudo apt install --reinstall python3-pkg-resources python3-setuptools
    pipenv shell
    pipenv install scikit-learn flask mlflow setuptools --python=3.12
    ```
- Start the server
    ```bash
    mlflow server --host 0.0.0.0 -p 5100 --backend-store-uri=sqlite:///mlflow.db --default-artifact-root=s3://mlflow-artifacts-joses/
    ```