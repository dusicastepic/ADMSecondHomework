import pandas as pd
import numpy as np

# RQ1

def compute_daily_average (df_names):
    """
    Compute the average number of trips recorded each day
    input:
    - list of the names of datasets
    output:
    - list of the daily average trips per each month
    """
    
    #initializing the month and the daily average list
    month = 1
    daily_average_lst = []
    
    for i in range(len(df_names)):
        # load the ith dataframe, taking only the t_pickup_datetime column
        df = pd.read_csv(df_names[i],usecols= ['tpep_pickup_datetime'], parse_dates= ["tpep_pickup_datetime"])
        
        # cleaning the attribute: removing years different from 2018 and months different from ith month
        df[(df['tpep_pickup_datetime'].dt.year == 2018) & (df['tpep_pickup_datetime'].dt.month == month)]
        
        # appending the average computed as the len of the dataframe / the last day of the month
        daily_average_lst.append(df.shape[0] // df["tpep_pickup_datetime"].iloc[-1].day)
        
        month += 1
    
    return daily_average_lst
