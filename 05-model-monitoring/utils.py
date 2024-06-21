import pandas as pd
from joblib import load

def preprocess_data(df,
                    target_col="duration_min",
                    feat_cols=["passenger_count", "trip_distance", 
                               "fare_amount", "total_amount",
                               "PULocationID", "DOLocationID"]):
    df["duration_min"] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration_min = df.duration_min.apply(lambda td : float(td.total_seconds())/60)
    df = df[(df.duration_min >= 0) & (df.duration_min <= 60)]
    df = df[(df.passenger_count > 0) & (df.passenger_count <= 8)]

    df_train = df[:30000].reset_index(drop=True)
    df_val = df[30000:].reset_index(drop=True)

    with open("models/lin_reg.bin", "rb") as f_in:
        model = load(f_in)
    
    df_train["prediction"] = model.predict(df_train[feat_cols])
    df_val["prediction"] = model.predict(df_val[feat_cols])
    
    return df_train,df_val