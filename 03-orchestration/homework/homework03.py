import pandas as pd
import pickle
import pathlib
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error 
from sklearn.linear_model import LinearRegression

import mlflow

import prefect
from prefect import flow, task


@task(retries=3, retry_delay_seconds=2)
def read_dataframe(filename):
    logger = prefect.get_run_logger()

    df = pd.read_parquet(filename)

    logger.info(f"Original Data Shape: {df.shape}")

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)

    logger.info(f"Processed Data Shape: {df.shape}")
    
    return df

@task
def add_features(df_train: pd.DataFrame):
    """Add features to the model"""
    # df_train["PU_DO"] = df_train["PULocationID"] + "_" + df_train["DOLocationID"]
    
    categorical = ['PULocationID', 'DOLocationID']
    numerical = ["trip_distance"]

    dv = DictVectorizer()

    # train_dicts = df_train[categorical + numerical].to_dict(orient="records")
    train_dicts = df_train[categorical].to_dict(orient="records")
    X_train = dv.fit_transform(train_dicts)

    y_train = df_train["duration"].values
    return X_train, y_train, dv

@task(log_prints=True)
def train(X_train, y_train, dv):
    logger = prefect.get_run_logger()

    with mlflow.start_run():
        lr = LinearRegression()
        lr.fit(X_train, y_train)

        logger.info(f"Linear Regression Model Intercepr: {lr.intercept_}")

        pathlib.Path("models").mkdir(exist_ok=True)
        with open("models/preprocessor.b", "wb") as f_out:
            pickle.dump(dv, f_out)
        mlflow.log_artifact("models/preprocessor.b", artifact_path="preprocessor")

        mlflow.sklearn.log_model(lr, artifact_path="model_mlflow")
    return 


@flow
def main_flow(
    train_path: str = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet",
    # val_path: str = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet",
) -> None:
    """The main training pipeline"""

    # MLflow settings
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("hw3-orchestration")

    # Load
    df_train = read_dataframe(train_path)

    # Transform
    X_train, y_train, dv = add_features(df_train)

    # Train
    train(X_train, y_train, dv)


if __name__ == "__main__":
    print(f"For this homework, I use orchestration tool Prefect.And the version is: {prefect.__version__}")

    main_flow()