"""Run the analysis over the monthly exports in data/ and write the plots to plots/.

    python analyze.py [--cats 3] [--data data] [--out plots]

Each file is one month of the Whisker app's activity export, named YYYY-MM.csv; the year comes from
the name because the export's timestamps carry none.
"""
import argparse
import pathlib

import pandas as pd

from catweights import (csv_to_df, identify_and_clean, plot_by_hour, plot_cleaned_scatter,
                        plot_scatter, save)


def load(data_dir):
    frames = [csv_to_df(f, f.stem[:4]) for f in sorted(pathlib.Path(data_dir).glob('*.csv'))]
    df = pd.concat(frames, ignore_index=True)
    return df.drop_duplicates(subset=['Date', 'Weight']).sort_values('Date').reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cats', type=int, default=3)
    ap.add_argument('--data', default='data')
    ap.add_argument('--out', default='plots')
    args = ap.parse_args()

    raw = load(args.data)[['Date', 'Weight']]
    out = pathlib.Path(args.out)
    out.mkdir(exist_ok=True)
    save(plot_scatter(raw.copy()), out / 'raw.png')

    df, lines = identify_and_clean(raw.copy(), args.cats)
    save(plot_cleaned_scatter(df.copy()), out / 'cats.png')
    save(plot_by_hour(df.copy()), out / 'by_hour.png')

    print(f'{len(raw)} weigh-ins, {raw.Date.min():%Y-%m-%d} to {raw.Date.max():%Y-%m-%d}; '
          f'{len(raw) - len(df)} dropped as outliers')
    month = 30.44 * 86400
    for cat in sorted(lines):
        slope, intercept = lines[cat]
        visits = df[df['Cat'] == cat]
        start = slope * visits['x'].min() + intercept
        end = slope * visits['x'].max() + intercept
        print(f'cat {cat}: {len(visits)} visits, {start:.1f} lb to {end:.1f} lb '
              f'({slope * month:+.2f} lb/month)')


if __name__ == '__main__':
    main()
