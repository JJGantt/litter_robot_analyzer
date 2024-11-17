import os
import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')

from auth import login_required
from db import get_db, get_db_connection
from logic import csv_to_df, plot_scatter, identify_and_clean, plot_cleaned_scatter, plot_by_hour


bp = Blueprint('profile', __name__)

@bp.route('/')
def index():
    
    if hasattr(g, 'user') and g.user:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT poopdate, weight FROM data WHERE userid = %s;', (g.user['user_id'],))
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        df = pd.DataFrame(data)

        if df.shape[0] == 0:
            flash("Please upload data to begin")
            return render_template('profile/index.html', is_data=False)
        
        df.columns = ['Date', 'Weight']
        df.Date = df.Date.apply(lambda x: pd.to_datetime(x, unit='s'))

        print('#*********trying to plot scatter')
        plot_scatter(df.copy())
        df, _ = identify_and_clean(df, 3)

        print('#*********trying to plot cleaned scatter')
        plot_cleaned_scatter(df.copy())
        print('#*********trying hourly plot')
        plot_by_hour(df.copy())

        df.drop(columns='x')
        df.sort_values(by='Date', inplace=True)

        return render_template('profile/index.html', data=df.to_html(), is_data=True)
    
    #return redirect('auth/login')
    return render_template('profile/index.html', is_data=False)

@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    this_year = datetime.date.today().year
    if request.method == 'POST':
        user_id = session.get('user_id')
        files = request.files.getlist('files')
        year = request.form['year']
        if not year:
            year = this_year
        conn = get_db_connection()
        cur = conn.cursor()


        print(f'****connected to db***** conn={conn}')
        #get list of dates already in database
        cur.execute('SELECT poopdate FROM data WHERE userid = %s;', (user_id,))
        dates = list(cur.fetchall())

        for f in files:
            df = csv_to_df(f, year)
            for i, row in df.iterrows():
                date = row.Date.timestamp()
                if (date,) not in dates:
                    cur.execute(
                        'INSERT INTO data (userid, poopdate, weight)'
                        'VALUES (%s, %s, %s)',
                        (user_id, int(date), row.Weight)
                    )
                    conn.commit()
        cur.close()
        conn.close()
        
        return redirect(url_for('index'))
        
    return render_template('profile/upload.html', this_year=this_year)

@bp.route('/delete', methods=['GET', 'POST'])
def delete():
    start='start'
    end='end'
    if request.method == 'POST':
        user_id = session.get('user_id')
        start = pd.to_datetime(request.form['start']).timestamp()
        end = pd.to_datetime(request.form['end']).timestamp()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'DELETE FROM data WHERE userid=%s ' 
            'AND poopdate BETWEEN %s AND %s;',
            (user_id, start, end)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('index'))

    return render_template('profile/delete.html')

@bp.route('/delete/all', methods=['POST'])
def delete_all():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'DELETE FROM data WHERE userid = %s;', (session.get('user_id'),)
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('index'))
    




