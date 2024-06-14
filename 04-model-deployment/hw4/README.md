### Homework
Use the `starter.ipynb` notebook
1. Check the prediction standard deviation with `np.std()` - *6.24*
2. Check the file size with `ls -al` - *68641674*
3. Convert notebook to script`!jupyter nbconvert --to script starter.ipynb`
4. Scikit-learn v1.5.0 hash `"sha256:057b991ac64b3e75c9c04b5f9395eaf19a6179244c089afdebaad98264bff37c"`
5. Only `["PULocationID", "DOLocationID"]` should be used as features. Generate the predictions for ***April 2023*** with `python score.py yellow 2023 4`. It should return a json like
    ```json
    {
      "score": "8.4396",
      "mean pred dur": "14.29 minutes"
    }
    ```
6. Build a docker image `docker build -t zmcp24-ride-dur:hw4 .` and run it with `docker run -it --rm zmcp24-ride-dur:hw4`. The docker environment essentially runs `python score.py yellow 2023 5` as the final command. This should print out a json object that resembles
    ```json
    {
      "score": "19.3376",
      "mean pred dur": "0.19 minutes"
    }
    ```
    The container is deleted immediately it finishes running. Seems like it give a different result from the `model.bin` file on github.

The upload to S3 bucket is not graded but aws access via docker was demonstrated in the model scoring workflow.