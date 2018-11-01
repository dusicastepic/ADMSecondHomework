import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from collections import defaultdict # see function compute_borough_averages

# RQ1 functions

def clean_dataframe(df, month):
    """
    Clean the dataframe, removing wrong dates and wrong taxy's trips
    input:
    - dataframe
    - month which correspond the dataframe
    output:
    - cleaned dataframe
    """
    
    #removing years different from 2018 and months different from ith month
    df = df[(df['tpep_pickup_datetime'].dt.year == 2018) & (df['tpep_pickup_datetime'].dt.month == month)]
        
    # removing races with total_amount > 0
    df = df[(df['total_amount'] > 0)]

    return df


def make_new_csv (df_names):
    """
    Make new csv files after cleaning each datasets
    input:
    - dataframe names' paths
    """

    df_old_names =['old_data/yellow_tripdata_2018-01.csv','old_data/yellow_tripdata_2018-02.csv',
                   'old_data/yellow_tripdata_2018-03.csv','old_data/yellow_tripdata_2018-04.csv',
                   'old_data/yellow_tripdata_2018-05.csv','old_data/yellow_tripdata_2018-06.csv']

    for i in range(len(df_names)):
        df = pd.read_csv(df_old_names[i], parse_dates= ["tpep_pickup_datetime"])
        # cleaning function
        df = clean_dataframe(df,i+1)
        df.to_csv(df_names[i])

    return



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
    # values: each value contains a list with daily average for each month for its key (borough)
    borough_averages = defaultdict(list)
    
    # defining the days for each month (to compute the average)
    month_days = [31, 28, 31, 30, 31, 30]
    
    for i in range(len(df_names)):

        df = pd.read_csv(df_names[i], usecols= ['tpep_pickup_datetime', 'total_amount', 'PULocationID', ],
                         parse_dates= ["tpep_pickup_datetime"])

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


def plot_boroug_averages(borough_averages, months):
    """
    Plot all the daily average for each borought
    input:
    - borought_averages: a dictionary with lists of averages
    - list of months
    """
    
    # Manhattan
    f = plt.figure()
    plt.grid(color = 'lightgray', linestyle='-.')
    plt.plot(months, borough_averages['Manhattan'], 'o', color = 'crimson', markersize = 12)
    #plt.bar(months, borough_averages['Manhattan'])
    plt.xlabel("months")
    plt.ylabel("daily_average")
    plt.title("Manhattan daily_average")
    f.set_figwidth(14)
    f.set_figheight(5)

    f = plt.figure()
    plt.grid(color = 'lightgray', linestyle='-.')
    plt.plot(months, borough_averages['Queens'], 'o', color = 'darkcyan', markersize = 12)
    #plt.bar(months, borough_averages['Manhattan'])
    plt.xlabel("months")
    plt.ylabel("daily_average")
    plt.title("Queens daily_average")
    f.set_figwidth(14)
    f.set_figheight(5)

    f = plt.figure()
    plt.grid(color = 'lightgray', linestyle='-.')
    plt.plot(months, borough_averages['Brooklyn'], 'o', color = 'orange', markersize = 12, label = 'Brooklyn')
    plt.plot(months, borough_averages['Unknown'], 'o', color = 'mediumseagreen', markersize = 12, label = 'Unknown')
    plt.legend()
    #plt.bar(months, borough_averages['Manhattan'])
    plt.xlabel("months")
    plt.ylabel("daily_average")
    plt.title("Brooklyn and Unknown daily_average")
    f.set_figwidth(14)
    f.set_figheight(5)

    f = plt.figure()
    plt.grid(color = 'lightgray', linestyle='-.')
    plt.plot(months, borough_averages['EWR'], 'o', color = 'violet', markersize = 12, label = 'EWR')
    plt.plot(months, borough_averages['Staten Island'], 'o', color = 'coral', markersize = 12, label = 'Staten Island')
    plt.legend()
    #plt.bar(months, borough_averages['Manhattan'])
    plt.xlabel("months")
    plt.ylabel("daily_average")
    plt.title("EWR and Staten Island daily_average")
    f.set_figwidth(14)
    f.set_figheight(5)

    return


def passengers_NY_all_months (df_names):
    """
        Returns the dataframe with two colums:
        tpep_pickup_datetime, passenger_count
        """
    df = pd.DataFrame()
    
    for i in range (len(df_names)):
        temp = pd.read_csv(df_names[i], usecols= ['tpep_pickup_datetime', 'passenger_count', 'PULocationID'],
                           parse_dates= ["tpep_pickup_datetime"])
                           
        df = df.append(temp)
    
    return df


def plot_NY_24_hours(df):
    """
    plot the hourly number of passengers for whole NY city
    """
    
    temp = df.drop('PULocationID',axis=1)
    f = plt.figure()
    temp.set_index("tpep_pickup_datetime",inplace=True)
    temp.groupby(temp.index.hour).sum().plot(kind = 'bar')
    temp.reset_index(inplace=True)
    f.set_figheight(6)
    f.set_figwidth(12)
    return


def time_slots(x):
    """
    function used with apply to select datatime
    """
    if 1 <= x < 6:
        return '01-06'
    elif 6 <= x < 12:
        return '06-12'
    elif 12 <= x < 17:
        return '12-17'
    elif 17 <= x < 20:
        return '17-20'
    else:
        return '20-01'



def time_slots_and_plot (df, color):
    """
    Groups the dataframe by the index hour,
    then with apply group it for time slots
    input:
    - df and the color of the instogram
    output:
    - plot of the passengers for every hours per whole NYC
    """
    # temporary df copied by the original one df
    temp = df.drop('PULocationID',axis=1)
    
    temp.set_index("tpep_pickup_datetime",inplace=True)
    temp=temp.groupby(temp.index.hour).sum()
    temp.reset_index(inplace=True)
    temp['tpep_pickup_datetime'] = temp.tpep_pickup_datetime.apply(time_slots)
    temp = temp.groupby(temp.tpep_pickup_datetime).sum()
    temp.plot(kind='bar',color=color)
    
    
    return


def passengers_for_each_borough (df, borough_lst, taxi_zone_lookup):
    """
    Same function of time_slot_and_plot, but it considers borough
    input:
    - df
    - borough list containing the borough
    - taxi_zone_lookup to merge with df to match taxi trips and boroughs
    output:
    - borough plot for each borough
    """
    plots_colors = ['royalblue', 'orange', 'violet', 'crimson', 'darkcyan', 'coral', 'mediumseagreen']
    
    df = pd.merge(df,taxi_zone_lookup, how = "left", left_on="PULocationID", right_on= "LocationID")
    df.drop(['PULocationID','LocationID'],axis=1,inplace=True)
    df = df.groupby(["Borough","tpep_pickup_datetime"]).sum()
    
    # for every sub dataframe (grouped by borough)
    for i in range(len(borough_lst)):
        
        # temp is our new sub dataframe, referred to a borough
        temp = df.loc[borough_lst[i]]
        temp = temp.groupby(temp.index.hour).sum()
        temp.reset_index(inplace=True)
        temp['tpep_pickup_datetime'] = temp.tpep_pickup_datetime.apply(time_slots)
        temp = temp.groupby('tpep_pickup_datetime').sum()
        
        #f = plt.figure()
        temp.plot(figsize=(11,5),kind='bar',color=plots_colors[i])
        plt.grid(color = 'lightgray', linestyle='-.')
        plt.xlabel("time slots")
        plt.ylabel("passengers in %s" %borough_lst[i])
        plt.title("%s" %borough_lst[i])

    return
