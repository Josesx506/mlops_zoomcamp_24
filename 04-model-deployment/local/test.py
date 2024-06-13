from local_predict import prepare_features, predict

ride = {
    "PULocationID": 10,
    "DOLocationID": 50,
    "trip_distance": 20 
}

pred = predict(prepare_features(ride))

print(pred)