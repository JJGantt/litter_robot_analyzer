import pandas as pd
import os

directory = 'static/csvs'

colnames = ['Action', 'Date', 'Weight']

df_list = []
for filename in os.listdir(directory):
    df = pd.read_csv(filename, names=colnames, index_col=None, header=0)
    df_list.append(df)

poop_df = pd.concat(df_list, axis=0, ignore_index=True)