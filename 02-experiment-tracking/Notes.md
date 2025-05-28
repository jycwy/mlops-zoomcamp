# Experiment Tracking

## 2.1 Experiment tracking intro

## 2.2 Getting started with MLflow
- Launch MLflow UI with a Backend Store:

`
mlflow ui --backend-store-uri sqlite:///mlflow.db
`

- Setup MLflow experiment tracking

`
import mlflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("nyc-taxi-experiment")
`

- Log the predications, show in MLflows UI


## 2.3 Experiment tracking with MLflow
- Add parameter tuning: hyperopt library

- show how it looks in MLflow

- Select the best hyper parameter combination

- autolog

## 2.4 Model management

- the ML workflow lifecycle
<img src="../imgs/ML Lifecycle.png">

- two ways to save the model in mlflow
<img src="../imgs/Logging models.png">

- load the models stored in mlflow
    - Way 1: load model as a function that can directlly call
    - Way 2: load model as xhboost model
<img src="../imgs/MLflow Model Format.png">

## 2.5 Model registry
- model registry
<img src="../imgs/Model Registry.png">
These model are production ready

- MLflow client
<img src="../imgs/MLflowClient.png">


<img src="../imgs/Model managment in MLflow.png">

## 2.6 MLflow in Practice
- Configuring MLflow

<img src="../imgs/Configuring MLflow.png">

- Remote tracking server
<img src="../imgs/RemoteTrackingServer.png">

- Issues
<img src="../imgs/RemoteMLflowServer Issues.png">