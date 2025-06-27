import pytest
import batch
import pandas as pd
from datetime import datetime
from deepdiff import DeepDiff


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


def test_prepare_data():
    # Test data
    data = [
        (None, None, dt(1, 1), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
    ]

    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df = pd.DataFrame(data, columns=columns)
    categorical = ['PULocationID', 'DOLocationID']
    
    # Call the function
    actual_result = batch.prepare_data(df, categorical)
    
    # Expected result after transformations:
    # Row 0: duration = 9 minutes (1:01 to 1:10), kept, PU/DO = -1/-1
    # Row 1: duration = 8 minutes (1:02 to 1:10), kept, PU/DO = 1/1  
    # Row 2: duration = 59 seconds = ~0.98 minutes, filtered out (< 1 minute)
    # Row 3: duration = 60 minutes + 1 second = ~60.017 minutes, filtered out (> 60 minutes)
    
    expected_data = [
        ('-1', '-1', dt(1, 1), dt(1, 10), 9.0),
        ('1', '1', dt(1, 2), dt(1, 10), 8.0),
    ]
    
    expected_columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime', 'duration']
    expected_result = pd.DataFrame(expected_data, columns=expected_columns)
    expected_result.index = [0, 1]  # Reset index to match filtered result
    
    # Convert to dictionaries for comparison with deepdiff
    actual_dict = actual_result.to_dict('records')
    expected_dict = expected_result.to_dict('records')
    
    # Use deepdiff to compare the results
    diff = DeepDiff(expected_dict, actual_dict, ignore_order=True)
    
    # Assert no differences found
    assert not diff, f"DataFrames are different: {diff}"