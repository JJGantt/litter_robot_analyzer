"""Separate the weigh-ins of several cats sharing one Litter-Robot scale.

The robot logs every visit's weight but not which cat it was. Each cat's weight drifts over months,
so a fixed weight band per cat mislabels visits as the cats gain or lose. Instead each cat gets a
trend line: visits go to the nearest line, the lines are refit on what they were given, and local
outliers (a cat stepping half on, litter shifting) are dropped between passes.
"""
import numpy as np
import pandas as pd
from datetime import datetime
from scipy.stats import linregress
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [10, 5]

def to_date_object(date, year):
    new_date = f'{year} {date}'
    date_object = datetime.strptime(new_date, '%Y %m/%d %I:%M%p')
    return date_object

def weight_to_float(weight):
    return float(weight.split()[0]) if weight != '-' else 0


def csv_to_df(csv, year):
    """One month of the Whisker app's activity export. Its timestamps carry no year."""
    colnames = ['Action', 'Date', 'Weight']
    df = pd.read_csv(csv, names=colnames, index_col=None, header=0)

    df = df[df['Weight'] != '-']

    df.Date = df.Date.apply(lambda x: to_date_object(x, year))
    df.Weight = df.Weight.apply(weight_to_float)

    return df

def save(fig, path):
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)

def plot_scatter(df):
    df['Date '] = df.Date
    plot = df.plot(kind='scatter', x='Date ', y='Weight', s=8)
    plot.set_title('Every recorded visit')
    plot.set_ylabel('Weight (lb)')
    return plot.figure

def plot_cleaned_scatter(df):
    df['Date '] = df.Date
    plot = df.plot(kind='scatter', x='Date ', y='Weight', c=df['Cat'], cmap='tab10', colorbar=False, s=8)
    plot.set_title('Visits assigned to each cat, outliers removed')
    plot.set_ylabel('Weight (lb)')
    return plot.figure

def plot_by_hour(df):
    df['Month'] = df['Date'].dt.month
    df['Hour'] = df['Date'].dt.hour
    df['Minute'] = df['Date'].dt.minute

    grouped_df = df.groupby(['Hour', 'Cat']).size().reset_index(name='count')
    by_hour_df = grouped_df.pivot(index='Hour', columns='Cat', values='count')

    plot = by_hour_df.plot(kind='line', marker='o')
    plot.set_xticks(by_hour_df.index)
    plot.set_title('Visits by hour of day, per cat')
    plot.set_ylabel('Visits')
    return plot.figure

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
