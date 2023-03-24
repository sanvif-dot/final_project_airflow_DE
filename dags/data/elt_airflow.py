
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

import os
import pandas as pd
from datetime import datetime,date

default_args = {
    'owner': 'Sanvi',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 22),
}

dag = DAG(
    'etl_to_db',
    default_args=default_args,
    description='Extract CSV files, transform the date format, and load the data into a PostgreSQL database by creating a table.',
    schedule_interval=None,
)

def extract_transform_load(**kwargs):
    # Extract data from CSV files
    file1 = pd.read_csv(os.path.join('airflow-fp/dags/data', 'precipitation.csv'))
    file2 = pd.read_csv(os.path.join('airflow-fp/dags/data', 'temperature.csv'))

    # Transform data by converting date column format
    file1['date'] = pd.to_datetime(file1['date'], format='%m/%d/%Y')
    file2['date'] = pd.to_datetime(file2['date'], format='%m/%d/%Y')

    # Load data into PostgreSQL database by creating a table
    conn = psycopg2.connect(host='localhost', dbname='airflow', user='airflow', password='airflow')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS mytable (date DATE, value1 INTEGER, value2 INTEGER);')
    for _, row in file1.iterrows():
        cur.execute("INSERT INTO mytable (date, value1, value2) VALUES (%s, %s, %s);", (row['date'], row['value1'], row['value2']))
    for _, row in file2.iterrows():
        cur.execute("INSERT INTO mytable (date, value1, value2) VALUES (%s, %s, %s);", (row['date'], row['value1'], row['value2']))
    conn.commit()
    cur.close()
    conn.close()

extract_transform_load_task = PythonOperator(
    task_id='extract_transform_load',
    python_callable=extract_transform_load,
    dag=dag,
)

create_table_task = PostgresOperator(
    task_id='create_table',
    sql='CREATE TABLE IF NOT EXISTS mytable (date DATE, value1 INTEGER, value2 INTEGER);',
    postgres_conn_id='my_postgres_connection',
    dag=dag,
)

create_table_task >> extract_transform_load_task
