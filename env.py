from dotenv import load_dotenv
import os

cwd = os.getcwd()
env_path = f"{cwd}/envs"

if os.path.exists(env_path):
    load_dotenv(dotenv_path=f"{env_path}/db.env")
    load_dotenv(dotenv_path=f"{env_path}/ec2.env")

else:
    env_path = f"{os.path.dirname(cwd)}/envs"
    load_dotenv(dotenv_path=f"{env_path}/db.env")
    load_dotenv(dotenv_path=f"{env_path}/ec2.env")

# Import the environment variables
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT")
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI")