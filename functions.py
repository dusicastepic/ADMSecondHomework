import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time

import json
import folium
import geojson


from collections import defaultdict # see function compute_borough_averages

# Function that provides (and prints) some informations about the different csv files
def stats(df_names):
    
    for i in range(len(df_names)):

        df= pd.read_csv(df_names[i], parse_dates= ["tpep_pickup_datetime"])


        print ("mese %s" %str(i+1))
        print ("\tpayment_types     :",
               "[1:", str(df[df["payment_type"]== 1].shape[0]) + "]", "[2:", str(df[df["payment_type"]== 2].shape[0]) + "]",
               "[3:", str(df[df["payment_type"]== 3].shape[0]) + "]", "[4:", str(df[df["payment_type"]== 4].shape[0]) + "]",
               "[5:", str(df[df["payment_type"]== 5].shape[0]) + "]", "[6:", str(df[df["payment_type"]== 6].shape[0]) + "]"
              )



        print("\ttotal_amount == 0 : %i" %df[df["total_amount"] == 0].shape[0])
        print ("\tfare_amount == 0  :",df[df["fare_amount"]== 0].shape[0])
        print("\ttrip_distance == 0:",df[df["trip_distance"]== 0].shape[0])

        print("\tfare_amount == 0 and total_amount == 0 -->",
              df[(df["total_amount"] ==0) & (df["fare_amount"]==0)].shape[0])

        print("\tfare_amount == 0 or total_amount == 0 -->",
              df[(df["fare_amount"]==0) | (df["total_amount"] ==0)].shape[0])

        print("\tboth year and month different -->",
              df[(df['tpep_pickup_datetime'].dt.year != 2018) | (df['tpep_pickup_datetime'].dt.month != i+1)].shape[0] )
    return

# RQ1 functions

def clean_dataframe(df, month):
    """
    Clean the dataframe, removing wrong dates and wrong taxy's trips
    input:
    - dataframe
    - month which correspond the dataframe
    output:from scipy.stats import chi2_contingency, ttest_ind ,chisquare, kruskal, pearsonr
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

        df = pd.read_csv(df_names[i], usecols= ['tpep_pickup_datetime', 'total_amount', 'PULocationID'],
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
        
        # removing unknown dataframe
        df = df[df.index != 'Unknown']
        
        # for every index (key), compute the average and add it on the dictionary
        for key in df.index:
            borough_averages[key].append(int(df.loc[key][0]) // month_days[i])

    return borough_averages

def plot_daily_averages(daily_average_lst, months):
    """
    plots the daily average list
    """
    # plot daily_average_lst
    f = plt.figure()
    plt.xticks(range(1,7),months)
    plt.ylabel("daily_average")
    plt.xlabel("months")
    plt.title("Daily average for each month in NYC")
    plt.plot(range(1,7), daily_average_lst, '-o', markersize=13, color='royalblue')
    plt.grid(color ='lightgray', linestyle = '-.')
    f.set_figwidth(14)
    f.set_figheight(5)

    return

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
    plt.plot(months, borough_averages['Manhattan'], '-o', color = 'crimson', markersize = 12)
    #plt.bar(months, borough_averages['Manhattan'])
    plt.xlabel("months")
    plt.ylabel("daily_average")
    plt.title("Manhattan daily_average")
    f.set_figwidth(14)
    f.set_figheight(5)

    f = plt.figure()
    plt.grid(color = 'lightgray', linestyle='-.')
    plt.plot(months, borough_averages['Queens'], '-o', color = 'darkcyan', markersize = 12)
    #plt.bar(months, borough_averages['Manhattan'])
    plt.xlabel("months")
    plt.ylabel("daily_average")
    plt.title("Queens daily_average")
    f.set_figwidth(14)
    f.set_figheight(5)

    f = plt.figure()
    plt.grid(color = 'lightgray', linestyle='-.')
    plt.plot(months, borough_averages['Brooklyn'], '-o', color = 'orange', markersize = 12, label = 'Brooklyn')
    #plt.plot(months, borough_averages['Unknown'], '-o', color = 'mediumseagreen', markersize = 12, label = 'Unknown')
    plt.legend()
    #plt.bar(months, borough_averages['Manhattan'])
    plt.xlabel("months")
    plt.ylabel("daily_average")
    plt.title("Brooklyn daily_average")
    f.set_figwidth(14)
    f.set_figheight(5)

    f = plt.figure()
    plt.grid(color = 'lightgray', linestyle='-.')
    plt.plot(months, borough_averages['EWR'], '-o', color = 'violet', markersize = 12, label = 'EWR')
    plt.plot(months, borough_averages['Staten Island'], '-o', color = 'coral', markersize = 12, label = 'Staten Island')
    plt.legend()
    #plt.bar(months, borough_averages['Manhattan'])
    plt.xlabel("months")
    plt.ylabel("daily_average")
    plt.title("EWR and Staten Island daily_average")
    f.set_figwidth(14)
    f.set_figheight(5)

    return
##RQ2

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
    
    # A new temp dataframe with df without 'PULocationID' column
    temp = df.drop('PULocationID',axis=1)
    
    # Using the 'tpep_pickup_datetime' as index and groupying by index.hour
    temp.set_index("tpep_pickup_datetime",inplace=True)
    temp = temp.groupby(temp.index.hour).sum()
    
    # plotting the df
    f = plt.figure()
    ax = temp.plot(figsize=(15,6),kind='bar', color = "royalblue", zorder=3)
    
    # grids
    plt.grid(color = 'lightgray', linestyle='-.', zorder = 0)
    # setting label for x, y and the title
    plt.setp(ax,xlabel='hours', ylabel='amount of passengers [Mln]',
             title = 'NYC: amount of passengers per hours (in millions) from January to June 2018')
    
    # converting in million y values
    vals = ax.get_yticks()
    ax.set_yticklabels(['{:.2f}'.format(x*1e-6) for x in vals])

    plt.show()
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
    # temporary df copied by the original df (without column 'PULocationID')
    temp = df.drop('PULocationID',axis=1)
    
    # setting as index datetime
    temp.set_index("tpep_pickup_datetime",inplace=True)
    # grouping by hours (0-23)
    temp=temp.groupby(temp.index.hour).sum()
    # restoring the column 'tpep_pickup_datetime'
    temp.reset_index(inplace=True)
    # changig every hour in 'tpep_pickuptime' in the corresponding slot_time (Using time_slots)
    temp['tpep_pickup_datetime'] = temp.tpep_pickup_datetime.apply(time_slots)
    # groupying by time slots
    temp = temp.groupby(temp.tpep_pickup_datetime).sum()
    
    # plotting the result
    ax = temp.plot(figsize=(12,6), kind='bar',color=color, zorder=3)
    plt.grid(color = 'lightgray', linestyle='-.', zorder = 0)

    plt.setp(ax,xlabel='time_slots', ylabel='amount of passengers [Mln]',
             title = 'NYC: amount of passengers per time_slots (in millions) from January to June 2018')

    # converting in million y values
    vals = ax.get_yticks()
    ax.set_yticklabels(['{:.2f}'.format(x*1e-6) for x in vals])
    
    plt.show()
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
    # plots colors
    plots_colors = ['royalblue', 'orange', 'violet', 'crimson', 'darkcyan', 'coral', 'mediumseagreen']
    
    # merge df with taxi_zone_lookup
    df = pd.merge(df,taxi_zone_lookup, how = "left", left_on="PULocationID", right_on= "LocationID")
    df.drop(['PULocationID','LocationID'],axis=1,inplace=True)

    # groupby Borough and datetime
    df = df.groupby(["Borough","tpep_pickup_datetime"]).sum()
    
    # Now we have a dataframe grouped by boroughs
    
    # for every sub dataframe (grouped by borough)
    for i in range(len(borough_lst)):
        
        # temp is our new sub dataframe, referred to the i borough in borough list
        temp = df.loc[borough_lst[i]]
        # group them by hours
        temp = temp.groupby(temp.index.hour).sum()
        # restore tpep_pickup_datetime (contains the average for every hour)
        temp.reset_index(inplace=True)
        # make time slots
        temp['tpep_pickup_datetime'] = temp.tpep_pickup_datetime.apply(time_slots)
        # groupby time_slots
        temp = temp.groupby('tpep_pickup_datetime').sum()
        
        # make plot
        f = plt.figure()
        ax = temp.plot(figsize=(11,5),kind='bar',color=plots_colors[i], zorder=3)
        plt.grid(color = 'lightgray', linestyle='-.', zorder = 0)
        plt.xlabel("time slots")
        plt.ylabel("passengers in %s" %borough_lst[i])
        plt.title("amount of passengers in %s" %borough_lst[i])
    
        plt.show()

    return
###RQ3

def make_duration_df (df_names, taxi_zone_lookup):
    """
    Make the dataframe with colums 'durations' and 'Borough'
    input:
    - df name's list
    - taxi_zone_lookup
    output:
    - a new dataframe
    """
    # creating a new empty df
    trip_duration = pd.DataFrame()
    
    # appending rows to trip_duration df
    for i, df_name in enumerate(df_names):
        
        # load csv file
        df = pd.read_csv(df_name,usecols=['tpep_pickup_datetime','tpep_dropoff_datetime', 'PULocationID'],
                         parse_dates=["tpep_pickup_datetime",'tpep_dropoff_datetime'])
            
        # merge with lookup_table to get boroughs
        df = pd.merge(df,taxi_zone_lookup, how="left", left_on="PULocationID", right_on="LocationID")

        #drop out unused columns
        df.drop(['PULocationID', 'LocationID', 'Zone', 'service_zone'], axis=1, inplace=True)

        # make the column durations and put it into tpep_dropoff_datetime
        df['tpep_dropoff_datetime'] = ((df['tpep_dropoff_datetime']-df['tpep_pickup_datetime'])/np.timedelta64(1, 's')).astype(int)

        # drop out the other column tpep_pickup_datetime
        df.drop('tpep_pickup_datetime',axis=1,inplace=True)

        # append the duration at the new df
        trip_duration = trip_duration.append(df)
    
    
    # change the name 'tpep_dropoff_datetime' in 'durations'
    trip_duration.rename(columns={"tpep_dropoff_datetime":"durations"}, inplace=True)
    
    
    # filtering df values:
    # keep durations in range (2 min, 1h:30m)
    trip_duration = trip_duration[ (trip_duration['durations']>120) & (trip_duration['durations']<5400)]
    

    #return the new data_frame
    
    return trip_duration


# old function, not used now
def plot_durations(df,zone_name, bins = 3600):
    """
    plotting the durations' density for df dataframe
    input:
    - df
    - zone of the name (as a string)
    - bins: n of histogram's intervals (DEFAULT: 1000)
    """
    
    f = plt.figure()
    df['durations'].plot(kind='hist',edgecolor="black", density=True, color='lightgrey',bins=bins)
    plt.xlim(0,6000)
    plt.xlabel('seconds')
    plt.title('distribution of trip\'s durations for %s' %zone_name)
    f.set_figheight(7)
    f.set_figwidth(15)
    
    return

# old function, not used now
def plot_Boroughs_durations (df, borough_lst):
    """
    plot durations' density for each borow
    input:
    - df
    - borough list
    """
    for i in range(len(borough_lst)):
        
        temp = df[df['Borough'] == borough_lst[i]]
        
        # using the function plot durations:
        # due EWR and Staten Island have less trips, we use 100 bins instead
        # of the default value (1000)
        if (borough_lst[i] == 'EWR') or (borough_lst[i] == 'Staten Island'):
            plot_durations(temp, borough_lst[i], bins=100)
        else:
            plot_durations(temp, borough_lst[i])

    return


def plot_frequencies (column, zone_name, bins = 30, xlim = 28, color = 'darkcyan' ):
    """
    Plot duration frequencies
    input:
    - df single attribute
    - zone_name (string)
    - bins (def 30) xlim (def 29) color (def 'darkcyan')
    """
    
    temp = pd.DataFrame()
    temp['values'] = column
    
    temp['new_col'] = pd.cut(temp['values'], bins=bins,precision=0)
    temp = temp.groupby('new_col').count()
    
    x = [str(i) for i in temp.index]
    
    f = plt.figure()
    ax = plt.bar(x = x, height=temp['values'], color = color)
    plt.title('trips duration\'s frequency in %s' %zone_name)
    plt.xticks (list(range(xlim-1)), x , rotation=90)
    plt.xlim(-1,xlim)
    plt.xlabel('trips_duration in seconds')
    plt.ylabel('frequency')
    
    f.set_figheight(5)
    f.set_figwidth(13)
    
    plt.show()
    return

def Boroughs_durations_freq (df, borough_lst):
    """
    for each borough plot the durations frequencies
    using the func plot_frequencies()
    input:
    - df
    - borough_lst
    """
    plots_colors = ['royalblue', 'orange', 'mediumseagreen', 'crimson',
                    'darkcyan', 'coral', 'violet']
        
    for i in range(len(borough_lst)):
    
        temp = df[df['Borough'] == borough_lst[i]]
        
        if (borough_lst[i] == 'EWR') or (borough_lst[i] == 'Staten Island'):
            plot_frequencies(temp['durations'], borough_lst[i],color=plots_colors[i], bins=20, xlim=21)
        elif borough_lst[i] == 'Manhattan':
            plot_frequencies(temp['durations'],borough_lst[i],color=plots_colors[i], bins=45, xlim=36)
        elif (borough_lst[i] == 'Bronx') or (borough_lst[i] == 'Queens'):
            plot_frequencies(temp['durations'],borough_lst[i],color=plots_colors[i], bins=25, xlim=26 )

    return

####RQ4

def payments_per_borough(df_names,taxi_zone_lookup,borough_lst):
    """
    compute the contingency table for every payment type for each borough
    input:
    - list of names of csv file to open
    - borough_lst 
    output:
    - data frame of frequencies of each payment for every borough and the list of all possible payment types
    """
    payment_type=['Credit card','Cash','No charge','Dispute','Unknown','Voided trip']

    res=[] #list to store parts of dataframe grouped by Borough and payment_type

    for i,df_name in enumerate(df_names): #repeating it for every fail(aka month)
            # load the ith dataframe, taking only 2 columns
            df = pd.read_csv(df_name,usecols= ['payment_type','PULocationID'])
            
            # merging it with taxi_zone_lookup file(left-join) 
            df=pd.merge(df,taxi_zone_lookup,how='left',left_on='PULocationID',right_on='LocationID')

            res.append(df.groupby(['payment_type','Borough']).count().iloc[:,0]) 
    
    #concatenating the results for all months and summing the values for each payment type
    res=pd.DataFrame(pd.concat(res,axis=1).sum(axis=1))
    res.reset_index(inplace=True)
    contingency_table=res.pivot(index='Borough', columns='payment_type', values=0).fillna(0)
    #change name of columns (instead of numbers(1,...,6) names of payment types)
    contingency_table.columns = [payment_type[i-1] for i in contingency_table.columns] 
    
    return contingency_table,payment_type
        
        
def payment_type_per_borough_plot(contingency_table,payment_type_lst):
    """
    plots the payment types for each borough
    """
    colors=['r','orange','royalblue','g','violet','pink']
    # boroughs one by one
    for ind in range(contingency_table.shape[0]-1):
        row=contingency_table.iloc[ind,:] 
        fig=plt.figure()
        plt.xticks(range(1,len(contingency_table.columns)),payment_type_lst)
        plt.title('Payments types used in: '+row.name)
        plt.ylabel("payment_types")
        plt.grid(True)
        fig.set_size_inches(9, 6)
        ax=sns.pointplot(x=contingency_table.columns, y=row, markersize=13,color=colors[ind])
        plt.show()

def payment_types_NYC_plot(payment_type_all,payment_type_lst):
    """
    plots the payment types for all NYC
    """
    fig=plt.figure()
    plt.xticks(range(1,7),payment_type_lst)
    plt.ylabel("payment_types")
    plt.grid(True)
    plt.set_cmap("ocean")
    fig.set_size_inches(9, 6)
    for ind,val in enumerate(payment_type_all):
        plt.plot(range(ind+1,ind+2), payment_type_all[ind:ind+1], 'd',markersize=13)
        plt.annotate(val,xy=[ind+1.1,val])
    plt.show()


#####RQ5

def duration_distance_df (df_names):
    """
        return a dataframe with trip duration and distances
        input:
        - df_names list
        output
        - new dataframe
        """
    
    res_df=pd.DataFrame()
    
    for i,df_name in enumerate (df_names):
        # load the ith dataframe, taking only the t_pickup_datetime column
        df = pd.read_csv(df_name,usecols= ['tpep_pickup_datetime','tpep_dropoff_datetime','trip_distance'],
                         parse_dates= ["tpep_pickup_datetime",'tpep_dropoff_datetime'])

        df['trip_duration']= ((df['tpep_dropoff_datetime']-df['tpep_pickup_datetime'])/ np.timedelta64(1, 's')).astype(int)


        res_df=res_df.append(df.loc[:,['trip_duration','trip_distance']])

    # filtering duration
    res_df = res_df[(res_df['trip_duration'] > 120) & (res_df['trip_duration'] < 3600*2)]
    # filtering distance
    res_df= res_df[(res_df['trip_distance'] > 1.2 )&(res_df['trip_distance'] < 50)]
    
    return res_df

def plot_duration_distance_freq (df):
    """
    plot duration and distance frequencies
    input:
    - df with trip_distance and trip_duration
    """
    
    f = plt.figure()
    ax1 = f.add_subplot(221)
    ax2 = f.add_subplot(222)
    
    df['trip_duration'].plot(kind = 'kde',color='darkgreen',ax=ax1, xlim=(0,4000))
    df['trip_duration'].plot(kind='hist',edgecolor="black", density=True, color='honeydew',bins=40,ax=ax1)
    ax1.set_xlabel('time [s]')
    ax1.title.set_text('trip duration frequency')
    
    
    df['trip_distance'].plot(kind = 'kde',color='darkblue',ax=ax2, xlim = (0,30))
    df['trip_distance'].plot(kind='hist',edgecolor="black", density=True, color='lavender',bins=30,ax=ax2)
    
    ax2.title.set_text('trip distance frequency')
    ax2.set_xlabel('miles')
    f.set_figheight(14)
    f.set_figwidth(14)
    plt.show()
    
    return

# CQ1

def make_df_price_per_mile(df_names,taxi_zone_lookup):
    """
    filter csv files, return a dataframe:
    input:
    df_names, table_taxi
    -output: following attributes:
    'price per mile', 'trip_distance', 'borough'
    
    """

    temp=pd.DataFrame() #list to store parts of dataframe grouped by Borough and payment_type

    for i,df_name in enumerate(df_names): #repeating it for every fail(aka month)
        # load the ith dataframe
        df = pd.read_csv(df_name,usecols= ['tpep_pickup_datetime','tpep_dropoff_datetime','trip_distance','PULocationID','fare_amount'],
                         parse_dates= ["tpep_pickup_datetime",'tpep_dropoff_datetime'])
            
        # making column trip duration
        df['trip_duration']= ((df['tpep_dropoff_datetime']-df['tpep_pickup_datetime'])/ np.timedelta64(1, 's')).astype(int)

        df['price_per_mile']=round(df['fare_amount']/df.trip_distance, 2)

        # dropping out some col
        df.drop(columns=['tpep_dropoff_datetime','tpep_pickup_datetime'], inplace=True)

        df.drop(columns=['trip_distance','fare_amount'], inplace=True)

        # merging it with taxi_zone_lookup file(left-join)
        df=pd.merge(df,taxi_zone_lookup,how='left',left_on='PULocationID',right_on='LocationID')

        df.drop(columns=['PULocationID','LocationID','Zone','service_zone'], inplace=True)
            
        temp = temp.append(df)

    # filtering trip_duration values
    temp = temp[(temp['trip_duration'] > 120) & (temp['trip_duration']<5400)]
    # filtering price_per_mile
    temp = temp[(temp['price_per_mile'] > 1.5) & (temp['price_per_mile'] < 30 )]
    return temp


def make_boro_dict (df, borough_lst):
    """
    return a dictionary with a dataframe for each borough
    output: df_dict with following attributes:
    'price per mile', 'trip_distance', 'borough'
    """
    boro_dict = {}

    for i in range (len(borough_lst)):
        boro_dict[i] = df[df['Borough'] == borough_lst[i]]

    return boro_dict


def mean_std_table (boro_dict,borough_lst, attribute):
    """
    make a table with means and std for each borough
    """
    mean_std_table = pd.DataFrame(columns= ['Borough', 'Mean', 'Std'])

    for i, boro in enumerate(boro_dict.values()):
        mean_std_table.loc[i] = [borough_lst[i], round(boro[attribute].mean(),3),
                                 round(boro[attribute].std(),3)]

    return mean_std_table

def plot_price_per_mile (boro_dict, borough_lst):
    
    fig, axes = plt.subplots (nrows=3, ncols=2)
    
    plots_colors = ['royalblue', 'orange', 'violet', 'crimson', 'darkcyan', 'coral', 'mediumseagreen']
    plt.setp(axes, xticks=np.arange(0, 15, step=1))
    
    for i, ax in enumerate(axes.flatten()):
        
        if (borough_lst[i] == 'Staten Island'):
            boro_dict[i]['price_per_mile'].plot(kind='hist',edgecolor="black", xlim = (1,15), ax = ax,color = plots_colors[i],
                                                density=True,bins=50, zorder = 3)
                                                
            ax.grid(color = 'lightgray', linestyle='-.', zorder = 0)
    
            ax.set_xlabel('%s - price per mile' %borough_lst[i])
        elif(borough_lst[i] == 'EWR'):
            boro_dict[i]['price_per_mile'].plot(kind='hist',edgecolor="black", xlim = (1,15), ax = ax,
                                                color = plots_colors[i],
                                                density=True,bins=100, zorder = 3)
                                                
            ax.grid(color = 'lightgray', linestyle='-.', zorder = 0)
            ax.set_xlabel('%s - price per mile' %borough_lst[i])
        else:
            boro_dict[i]['price_per_mile'].plot(kind='hist',edgecolor="black", xlim = (1,15), ax = ax,
                                                color = plots_colors[i],
                                                density=True,bins=100, zorder = 3)
                                                
            ax.grid(color = 'lightgray', linestyle='-.', zorder = 0)
            ax.set_xlabel('%s - price per mile' %borough_lst[i])

    fig.set_figheight(14)
    fig.set_figwidth(15)

    plt.show()

    return


def color_negative_red (value):
    
    if value <= 0.05:
        color = 'green'
    else:
        color = 'red'
    
    if value == 1:
        color = 'black'
    
    return ('color: %s' %color)


def p_value_table (boro_dict, borough_lst, attribute):
    
    p_value_table = pd.DataFrame(columns= borough_lst)

    for i, bor in enumerate(boro_dict):
        p_value_row_i = [round(ttest_ind(boro_dict[i][attribute], boro_dict[j][attribute])[1],3) for j in range(0,6)]
        p_value_table.loc[borough_lst[i]] = p_value_row_i

    return p_value_table.style.applymap(color_negative_red, subset= borough_lst)


def plot_p1 (boro_dict, borough_lst):
    
    fig, axes = plt.subplots (nrows=3, ncols=2)
    plt.setp(axes, xticks=np.arange(0, .05, step=0.005))
    
    plots_colors = ['royalblue', 'orange', 'violet', 'crimson', 'darkcyan', 'coral', 'mediumseagreen']
    
    for i, ax in enumerate(axes.flatten()):
        
        if (borough_lst[i] == 'Staten Island'):
            boro_dict[i]['p1'].plot(kind='hist',edgecolor="black", xlim = (-0.0,0.05), ax = ax,
                                    color = plots_colors[i],
                                    density=True,bins=25, zorder = 3)
            ax.grid(color = 'lightgray', linestyle='-.', zorder = 0)
            ax.set_xlabel('%s - p1' %borough_lst[i])
        
        elif(borough_lst[i] == 'EWR'):
            boro_dict[i]['p1'].plot(kind='hist',edgecolor="black", xlim = (-0.0,0.05), ax = ax,
                                    color = plots_colors[i],
                                    density=True,bins=40, zorder = 3)
            ax.grid(color = 'lightgray', linestyle='-.', zorder = 0)
            ax.set_xlabel('%s - p1' %borough_lst[i])
        else:
            boro_dict[i]['p1'].plot(kind='hist',edgecolor="black", xlim = (-.0,0.05), ax = ax,
                                    color = plots_colors[i],
                                    density=True,bins=100, zorder = 3)
            ax.grid(color = 'lightgray', linestyle='-.', zorder = 0)
            ax.set_xlabel('%s - p1' %borough_lst[i])
                                        
                                        
    fig.set_figheight(14)
    fig.set_figwidth(15)

    plt.show()
        
    return


# CQ2

def take_pickup_and_dropoff_zones(df_names, taxi_zone_lookup):
    """
        return the dataframe merged with taxi_zone_lookup
        input:
        - df_names (list of csv files)
        - taxi_zone_lookup (path of taxi_zone_lookup)
        output:
        - a dataframe
    """
    
    # dataframe to be load
    res=pd.DataFrame()
    
    for i,df_name in enumerate(df_names): #repeating it for every fail(aka month)
        # load the ith dataframe, taking only 2 columns
        df = pd.read_csv(df_name,usecols= ['PULocationID', 'DOLocationID'])
        
        # merging it with taxi_zone_lookup file(left-join)
        
        df=pd.merge(df,taxi_zone_lookup,how='left',left_on='PULocationID',right_on=['LocationID'])
            
        res=res.append(df)

    return res



def Locations_counter (df, type_of_LocID):
    """
        it counts in df the occurrences of each LocID contained in'type_of_LocID' (df's parameter)
        and returns them as a list. It's used for columns 'PULocationID' and 'DOLocationID'
        input:
        - df
        - type_of_locID
        output:
        - a list with 256 values (for each LocID)
    """
    
    #temp dataframe, it will take before the counters of PULocID and then DOLocID
    occurrencies = pd.DataFrame()
    
    #groupying by locationID (PULocationID or DOLocationID)
    occurrencies['LocID'] = df.groupby(type_of_LocID).count()['LocationID']
    
    new_lst = []
    
    for i in range (1,266):
        if i in occurrencies.index:
            new_lst.append(int(occurrencies.loc[i]))
        else:
            new_lst.append(0)

    return new_lst


def make_map(json_data, PU_DO_occurrencies, type_of_LocID):
    """
        it creates a folium map considering PU_DO_occurrencies dataframe and the
        type_of_LocID requested for the map (PULocationID or DOLocationID)
        input:
        - json_data file with the map
        - PU_DO_occurrencies: dataframe with attributes:
        'LocID' || 'PULocID_counts' || 'DOLocID_counts'
        - type_of_LocID requested for the map (PULocID_counts or DOLocID_counts)
    """
    
    #m = folium.Map(location=[40.7128, -74.0060],control_scale=True)
    # markers for airports
    m = folium.Map(location=[40.7128, -74.0060],control_scale=True, zoom_start=10.5)
    folium.Marker([40.64, -73.77], popup='John F. Kennedy International Airport').add_to(m)
    folium.Marker([40.7769, -73.8740], popup='LaGuardia Airport').add_to(m)
    
    # scale for the legend (referred to max_min values of PU_DO_occurrencies[type_of_LocID]
    threshold_scale = np.linspace(PU_DO_occurrencies[type_of_LocID].min(),
                                  PU_DO_occurrencies[type_of_LocID].max(),
                                  6, dtype=int).tolist()

    m.choropleth(geo_data=json_data, data=PU_DO_occurrencies,
               columns=['LocID',type_of_LocID],
               key_on='properties.LocationID',
               fill_color='YlOrRd', fill_opacity=0.7, line_opacity=0.2,
               legend_name='taxi pickup density', threshold_scale=threshold_scale)
               
    return m


def pickup_and_dropoff_maps(df_names, taxi_zone_lookup, json_filename):
    """
        creates two maps and return them into a list
        input:
        - df_names
        - taxi_zone_lookup
        - json_filename
        output:
        - list with two maps
    """
    
    #importing json data
    json_data = json.load(open(json_filename))
    
    # declaring the map list
    maps_list = []
    
    # creating a new data frame and load it
    df = pd.DataFrame()
    df = take_pickup_and_dropoff_zones(df_names,taxi_zone_lookup)
    
    # loading into a list the counter for each LocationID
    # we will put the two lists into a new dataframe
    PU_list = []
    DO_list = []
    
    PU_list = Locations_counter(df,'PULocationID')
    DO_list = Locations_counter(df,'DOLocationID')
    
    # df is not needed anymore
    del df
    
    # creating a new dataframe
    # PU_DO_occurrencies will contain 3 columns:
    # Location ID || PULocationID_counter || DOLocationID_counter
    PU_DO_occurrencies = pd.DataFrame()
    
    PU_DO_occurrencies['LocID'] = list(range(1,266))
    PU_DO_occurrencies['PULocID_counts'] = PU_list
    PU_DO_occurrencies['DOLocID_counts'] = DO_list
    
    maps_list.append(make_map(json_data,PU_DO_occurrencies, 'PULocID_counts'))
    maps_list.append(make_map(json_data,PU_DO_occurrencies, 'DOLocID_counts'))
    
    return maps_list
