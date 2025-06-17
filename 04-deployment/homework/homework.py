import pickle
import pandas as pd
import os
import argparse



categorical = ['PULocationID', 'DOLocationID']

def load_model(model_path):
    with open(model_path, 'rb') as f_in:
        dv, model = pickle.load(f_in)
    return dv, model

def read_data(filename, year, month):
    df = pd.read_parquet(filename)
    
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')

    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    
    return df

def predict(df, model_path):
    dicts = df[categorical].to_dict(orient='records')

    dv, model = load_model(model_path)
    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)

    # standard deviation of the predicted duration
    std_pred = pd.Series(y_pred).std()
    print(f"Standard deviation of the predicted duration: {std_pred}")

    # mean predicted duration
    mean_pred = pd.Series(y_pred).mean()
    print(f"Mean predicted duration: {mean_pred}")

    return y_pred


def save_results(df, output_file, y_pred):
    df_result = pd.DataFrame({
        'ride_id': df['ride_id'],
        'prediction': y_pred
    })

    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )

def run():
    parser = argparse.ArgumentParser(description='Predict taxi trip durations.')
    parser.add_argument('--year', type=int, required=True, help='Year of the trip data (e.g., 2022)')
    parser.add_argument('--month', type=int, required=True, choices=range(1, 13), help='Month of the trip data (1-12, e.g., 1 for January)')
    args = parser.parse_args()

    year = args.year
    month = args.month
    # run_id = args.run_id  # Uncomment if you add run_id as an argument

    print(f"Start taxi time duration prediction for data {year}-{month}")
    input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    output_file = f'output/yellow/{year:04d}-{month:02d}.parquet'
    model_path = 'model.bin'

    # Create the output directory if it doesn't exist
    os.makedirs('output/yellow', exist_ok=True) 

    df = read_data(input_file, year, month)
    y_pred = predict(df, model_path)
    save_results(df, output_file, y_pred)

if __name__ == '__main__':
    run()

   

