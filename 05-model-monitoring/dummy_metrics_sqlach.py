import io
import logging
import os
import random
import time
from uuid import uuid4
from datetime import datetime, timedelta

import pandas as pd
import psycopg
import pytz
from flask import Flask
from flask_migrate import init, migrate, upgrade, Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect,text

os.system("clear")
os.system("rm -rf migrations/")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

DB_HOST = "localhost"
DB_PORT = 5436
DB_USER = "postgres"
DB_PASSWORD = "example"
DB_NAME = "test" #grafana_monitoring
TABLE_NAME = "dummy_metrics"
SEND_TIMEOUT = 10 # seconds
database_path = f"postgresql://{DB_USER}:{DB_PASSWORD}@localhost:{DB_PORT}"

db = SQLAlchemy()
app = Flask(__name__)
local_tz = pytz.timezone("US/Eastern")


def reset_db():
    with psycopg.connect(f"host={DB_HOST} port={DB_PORT} user={DB_USER} password={DB_PASSWORD}", autocommit=True) as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'")
        # Check if the db is empty to reset it everytime
        if len(res.fetchall()) == 0:
            conn.execute(f"create database {DB_NAME};")
        else:
            conn.execute(f"drop database {DB_NAME};")
            conn.execute(f"create database {DB_NAME};")
        with psycopg.connect(f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}") as conn2:
            conn2.execute(f"drop table if exists {TABLE_NAME};")
            conn2.close()
        conn.close()

def migrate_db():
    init()
    migrate()
    upgrade()

def setup_db(app,  database_path=database_path):
    reset_db()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"{database_path}/{DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.app_context().push() # Minimize calling app_context() repeatedly
    db.app = app
    db.init_app(app)
    init_migrate = Migrate(app, db)
    migrate_db()

class DummyMetrics(db.Model):
    """
    This is the table that stores all the hair bookings made on the website
    """
    __tablename__ = TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    value1 = db.Column(db.Integer)
    value2 = db.Column(db.String)
    value3 = db.Column(db.Float)

    def __init__(self, timestamp, value1, value2, value3):
        self.timestamp = timestamp
        self.value1 = value1
        self.value2 = value2
        self.value3 = value3
    
    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            print(f"Error inserting into the database: {e}")
            db.session.rollback()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def format(self):
        return {
            "timestamp": self.timestamp,
            "value1": self.value1,
            "value2": self.value2,
            "value3": self.value3
            }

def calculate_dummy_metrics():
    dt = datetime.now(local_tz)
    value1 = random.randint(0,100)
    value2 = str(uuid4())
    value3 = random.random()

    entry = DummyMetrics(dt,value1,value2,value3)
    entry.insert()
    


def main():
    # Create a clean table that resets everytime
    setup_db(app)
    last_send = datetime.now() - timedelta(seconds=10)
    for i in range(100):
        calculate_dummy_metrics()

        new_send = datetime.now()
        seconds_elapsed = (new_send - last_send).total_seconds()
        if seconds_elapsed < SEND_TIMEOUT:
            time.sleep(SEND_TIMEOUT - seconds_elapsed)
        while last_send < new_send:
            last_send = last_send + timedelta(seconds=10)
        logging.info("data sent")

if __name__ == "__main__":
    main()