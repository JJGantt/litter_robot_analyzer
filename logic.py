import base64
import io

import numpy as np
import pandas as pd
from datetime import datetime
from scipy.stats import linregress
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [10, 5]

def to_date_object(date, year):
    #x = re.search(r"^\d*", date)
    #month = int(x.group())
    new_date = f'{year} {date}'
    date_object = datetime.strptime(new_date, '%Y %m/%d %I:%M%p')
    return date_object

def weight_to_float(weight):
    return float(weight.split()[0]) if weight != '-' else 0


def csv_to_df(csv, year):
    colnames = ['Action', 'Date', 'Weight']
    df = pd.read_csv(csv, names=colnames, index_col=None, header=0)

    df = df[df['Weight'] != '-']

    df.Date = df.Date.apply(lambda x: to_date_object(x, year))
    df.Weight = df.Weight.apply(weight_to_float)

    return df

# Plots are returned as PNG data URIs for the page to embed. Writing them to a
# shared file under static/ would serve one user's data to whoever loads that
# URL next. Each figure is closed once rendered; pyplot keeps every open figure
# alive for the life of the process otherwise.
def figure_data_uri(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('ascii')

def plot_scatter(df):
    df['Date '] = df.Date
    plot = df.plot(kind='scatter', x='Date ', y='Weight')
    return figure_data_uri(plot.figure)

def plot_cleaned_scatter(df):
    df['Date '] = df.Date
    plot = df.plot(kind='scatter', x='Date ', y='Weight', c=df['Cat'], cmap='tab10', colorbar=False)
    return figure_data_uri(plot.figure)

def plot_by_hour(df):
    df['Month'] = df['Date'].dt.month
    df['Hour'] = df['Date'].dt.hour
    df['Minute'] = df['Date'].dt.minute

    grouped_df = df.groupby(['Hour', 'Cat']).size().reset_index(name='count')
    by_hour_df = grouped_df.pivot(index='Hour', columns='Cat', values='count')

    plot = by_hour_df.plot(kind='line', marker='o')
    plot.set_xticks(by_hour_df.index)
    return figure_data_uri(plot.figure)

def identify_cats(input_df, cat_count, lines=None):
    df = input_df.copy()
    lines = {} if lines is None else lines

    if not lines:
        df = df.sort_values(by='Weight')

        num_data_points = len(df)
        n_tile_size = num_data_points // (cat_count * 3)
        n_tile_starts = [(3 * x + 1) * n_tile_size for x in range(cat_count)]

        for line_id, n_tile_start in enumerate(n_tile_starts): 
            n_tile_end = n_tile_start + n_tile_size
            line_data = df.iloc[n_tile_start:n_tile_end]

            slope, intercept, _, _, _ = linregress(line_data['x'], line_data['Weight'])
            lines[line_id] = (slope, intercept)

    residuals = np.zeros((len(df), cat_count))
    for line_id in range(cat_count):
        slope, intercept = lines[line_id]
        predicted_y = slope * df['x'] + intercept
        residuals[:, line_id] = df['Weight'] - predicted_y

    df['Cat'] = np.argmin(np.abs(residuals), axis=1)
    
    return df, lines

def clean_outliers(input_df):
    df = input_df.copy()
    df = df.sort_values(by='Date')
    
    window_size = 100 
    outliers_found = True
    while outliers_found:
        outlier_indices = []
        #iterating through slices of the data to determine local outliers
        for i in range(len(df)):
            start_index = max(0, i - window_size)
            end_index = min(len(df), i + window_size // 2 + 1)

            local_data = df.iloc[start_index:end_index]

            Q1 = local_data['Weight'].quantile(0.4)
            Q3 = local_data['Weight'].quantile(0.6)

            lower_bound = Q1 - 1
            upper_bound = Q3 + 1


            outliers = (local_data['Weight'] < lower_bound) | (local_data['Weight'] > upper_bound)

            for j in local_data.index[outliers]:
                outlier_indices.append(j)

        if outlier_indices:
            df = df.drop(outlier_indices).reset_index(drop=True)
        else:
            outliers_found = False
        
    return df

def identify_and_clean(input_df, cat_count):
    input_df['x'] = input_df.Date.apply(lambda x: x.timestamp())
    df = input_df.copy()
    lines = {}

    if cat_count > 1:
        for _ in range(2): #runs twice, providing a better guess at the lines to fit the data to on the second run     
            identified_df, lines = identify_cats(input_df, cat_count, lines)

            separated_dfs = [identified_df[identified_df['Cat'] == x] for x in range(cat_count)]
            cleaned_dfs = []

            for i, df in enumerate(separated_dfs):
                df = clean_outliers(df)            
                cleaned_dfs.append(df)
                
                slope, intercept, _, _, _ = linregress(df['x'], df['Weight'])
                lines[i] = (slope, intercept)

            df = pd.concat(cleaned_dfs)
    else:
        df = clean_outliers(df)
    
    return df, lines
