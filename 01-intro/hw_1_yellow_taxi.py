import os
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import root_mean_squared_error


def read_dataframe(path):
    df = pd.read_parquet(path)
    df.columns = [name.strip() for name in df.columns]
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    # Calculate the hire duration
    df["duration"] = df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    df["duration"] = df["duration"].apply(lambda td: round(td.total_seconds()/60, 4))
    print(df["duration"].std())
    # Filter out any bad records
    before = len(df)
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    after = len(df)
    print(f"% change: {round((after/before)*100,2)}")
    df = df.dropna(subset=["PULocationID","DOLocationID"]).reset_index(drop=True)
    # Clean up data types
    df = df.astype({"PULocationID":int,"DOLocationID":int})
    df["PU_DO"] = df.apply(lambda x: f"{x.PULocationID}_{x.DOLocationID}",axis=1)
    df = df.astype({"PULocationID":str,"DOLocationID":str})
    return df

df_train = read_dataframe("data/train/yellow_tripdata_2023-01.parquet")
df_val = read_dataframe("data/val/yellow_tripdata_2023-02.parquet")

# Select a subset of columns
train_cols,target_col = ["PULocationID","DOLocationID"],["duration"] #"PU_DO","trip_distance"

train_df = df_train[train_cols]
train_dicts = train_df.to_dict(orient="records")
val_df = df_val[train_cols]
val_dicts = val_df.to_dict(orient="records")

dv = DictVectorizer()

# Preprocess data
X_train = dv.fit_transform(train_dicts)
y_train = df_train[target_col].to_numpy().flatten()
X_val = dv.transform(val_dicts)
y_val = df_val[target_col].to_numpy().flatten()
print(f"Training Data has {X_train.shape[1]} columns")


########################### Linear Regression
lr = LinearRegression()
lr.fit(X_train,y_train)
y_pred = lr.predict(X_train)
mse = root_mean_squared_error(y_train, y_pred)
print(f"Linear Regression Train MSE:\t {mse:.4f}")
y_pred = lr.predict(X_val)
mse = root_mean_squared_error(y_val, y_pred)
print(f"Linear Regression Val MSE:\t {mse:.4f}")

with open("models/lin_reg.bin", "wb") as f_out:
    pickle.dump((dv,lr), f_out)

########################### Lasso Regression
# lr = Lasso(alpha=0.001)
# lr.fit(X_train,y_train)
# y_pred = lr.predict(X_val)
# mse = root_mean_squared_error(y_val, y_pred)
# print(f"Lasso Regression MSE:\t {mse:.4f}")

########################### Ridge Regression
lr = Ridge(alpha=0.001)
lr.fit(X_train,y_train)
y_pred = lr.predict(X_val)
mse = root_mean_squared_error(y_val, y_pred)
print(f"Ridge Regression MSE:\t {mse:.4f}")