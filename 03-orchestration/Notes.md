# 3.1 Machine Learning Pipelines
- Machine Learning Pipelines
<img src="imgs/Machine Learning Pipelines.png">

# Orchestration tool: Prefect
## Introduction to Workflow orchestration
- MLOps workflow
<img src="imgs/MLOps Workflow.png">

## Intruduction to Prefect
1. Introduction:

Task: like python function 
Flow: container for workflow logic

<img src="imgs/Prefect Term 1.png">
<img src="imgs/Prefect Term 2.png">

2. Clone github repo
[prefect-mlops-zoopcamp](https://github.com/discdiver/prefect-mlops-zoomcamp/tree/main)

3. Start a prefect server

`
prefect server start
`

4. Run a prefect flow

5. Checkout prefect UI

## Prefect Workflow
Add task & flow decorator on the python script

## Deploying your workflow (with local data)

<img src="imgs/development environment.png">

1. `prefect project init`
this would generate a 
prefect.yaml for configuring project / deployment build, push and pull steps

<img src="imgs/project yaml.png">

2. Set up the worker pool
    - create a worker poll in the UI page (a worker poll is to run a flow)
    - start the worker pool `prefect worker start -p worker_pool_name`


3. Deploy the flow
    ```
    prefect deploy --help
    prefect deploy py_file_name:flow_name -n name -p worker_poll_name 
    ```

4. Start a run of the deployed flow
    - from ui
    - command line `prefect deploytment run main-flow-s3/taxi_s3_data`

Note:
using this way may need to put the parquet data into the github data repo. So prefect can fetch the data from github.

## Working with deployments (with s3 data)
being familiar of prefect_aws library

Example: using amazon s3 to store the data
1. create credentials block and set up AWS S3 bucket
<img src="imgs/aws credentials and s3 bucket.png">

    the result can be viewed in prefect UI

    `prefect block ls` list all the blocks

    `prefect block type ls` list all the blocks and types

    `prefect block register -m prefect-aws` register all the prefect blocks defined in the prefect-aws module

    Note:
    ```
    In Prefect, a Block is a way to store and reuse configuration or credentials in a centralized, secure, and declarative manner.
    ```

2. Using S3Bucket in the task/flow code
    - load the s3 bucket
    - download from s3 bucket to local env

<img src="imgs/load s3 bucket.png">

3. Setting up deployments instead of doing manual deployment

    - config deployment.yaml
    - `prefect deploy --all` run in terminal
    
4. make a markdown artifacts
    - create_markdown_artifact()

5. push to github repo

    don't forget to github, as we defined in the prefect.yaml, the run would pull from github every time

6. other functions
    - set schedule
    - overwrite input parameters
    - ...

## Prefect Cloud

instead of running deployment run in local machine, using Prefect cloud to run your job
<img src="imgs/prefect cloud.png">

