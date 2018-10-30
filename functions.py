import pandas as pd
import numpy as np

from collections import defaultdict # see function compute_borough_averages

# RQ1 functions

def clean_dataframe(df, month):
    """
    Clean the dataframe, removing wrong dates and wrong taxy's trips
    input:
    - list of names of csv file to open
    - month which correspond the dataframe
    output:
    - cleaned dataframe'
    """
    
    #removing years different from 2018 and months different from ith month
    df = df[(df['tpep_pickup_datetime'].dt.year == 2018) & (df['tpep_pickup_datetime'].dt.month == month)]
        
    # removing races with total_amount > 0
    df = df[(df['total_amount'] > 0)]

    return df



def compute_daily_average (df_names):
    """
    Compute the average number of trips recorded each day
    input:
    - list of names of csv file to open
    output:
    - list of the daily average trips per each month
    """
    
    # init the daily average list
    daily_average_lst = []
    
    for i in range(len(df_names)):
        # load the ith dataframe, taking only the t_pickup_datetime and total_amount columns
        df = pd.read_csv(df_names[i], usecols= ['tpep_pickup_datetime', 'total_amount'],
                         parse_dates= ["tpep_pickup_datetime"])
        
        # cleaning dataframe (for the current month)
        df = clean_dataframe(df, i+1)
        
        # appending the average computed as the len of the dataframe / the last day of the month
        daily_average_lst.append(df.shape[0] // df["tpep_pickup_datetime"].iloc[-1].day)
    
    
    return daily_average_lst


def compute_borough_averages (df_names, taxi_zone_lookup):
    """
    compute the daily averages for each month for each borough
    input:
    - list of names of csv file to open
    - taxi_zone_lookup table
    output:
    - dictionary which contains for each borow the list of daily averages for each month
    """
    
    # dictionary:
    # keys: each borough
    # value: a list containing daily average for each month for that specific borough
    borough_averages = defaultdict(list)
    
    # defining the days for each month (to compute the average)
    month_days = [31, 28, 31, 30, 31, 30]
    
    for i in range(len(df_names)):

        df = pd.read_csv(df_names[i], usecols= ['tpep_pickup_datetime', 'total_amount', 'PULocationID', ],
                         parse_dates= ["tpep_pickup_datetime"])

        # cleaning the dataset of the month i+1 with function clean_dataframe()
        df = clean_dataframe(df,i+1)

        # dropping out the colums not needed anymore
        df.drop(['tpep_pickup_datetime', 'total_amount'], axis = 1, inplace= True)

        # merging PULocationID with taxi_zone_lookup table
        df = pd.merge(df, taxi_zone_lookup, how = 'left', left_on = 'PULocationID', right_on = 'LocationID')

        # dropping out other columns don't needed
        df.drop(['PULocationID', 'Zone', 'service_zone'], axis = 1, inplace = True)

        # grouping by Borough (indexing by Borough)
        # so we have only one column containing for each borough the total number of trips
        df = df.groupby("Borough").count()
        
        # for every index (key), compute the average and add it on the dictionary
        for key in df.index:
            borough_averages[key].append(int(df.loc[key][0]) // month_days[i])

    return borough_averages
