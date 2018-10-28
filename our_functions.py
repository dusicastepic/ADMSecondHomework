# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 22:33:43 2018

@author: Dusica
"""
def fetch_data(cols,parse_cols):
    list_DataFrames=[]
    df_names=['yellow_tripdata_2018-01.csv','yellow_tripdata_2018-02.csv',
          'yellow_tripdata_2018-03.csv','yellow_tripdata_2018-04.csv',
         'yellow_tripdata_2018-05.csv','yellow_tripdata_2018-06.csv']
    taxi_zone_lookup = pd.read_csv('data/taxi_zone_lookup.csv',usecols=['Borough','LocationID'])
    for i in df_names:
        list_DataFrames.append(pd.merge(pd.read_csv('data/'+str(i),usecols=cols,parse_dates=parse_cols)
                     ,taxi_zone_lookup, how="left",left_on="PULocationID",right_on="LocationID"))
    return list_DataFrames


def plot_daily_average():
    cols=['PULocationID','tpep_pickup_datetime']
    parse_cols=['tpep_pickup_datetime']
    list_DataFrames=fetch_data(cols,parse_cols)


    average_num_for_all_months=pd.DataFrame()
    list_data=[]
    for m,df in enumerate(list_DataFrames):
        num_of_days=df.iloc[-1]['tpep_pickup_datetime'].day
        df['month'] = df["tpep_pickup_datetime"].apply(lambda df : df.month)
        df=df[df['month']==m+1]
        average_number_of_rides=df.loc[:,['month','PULocationID']].groupby('month').count()/num_of_days 
        list_data.append(average_number_of_rides)
    average_num_for_all_months=average_num_for_all_months.append(list_data)
    my_xticks = ['January','February','March','April','May','June']
    plt.xticks(average_num_for_all_months.index, my_xticks)
    plt.plot(average_num_for_all_months.index,average_num_for_all_months.PULocationID, 'go')