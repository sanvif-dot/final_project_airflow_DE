# Import airflow modules
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator

# Import modules
import pandas as pd
import json
import psycopg2
import os

# Arguments
default_args = {
    'owner': 'Sanvi',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 21),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'csv_json_to_postgres',
    default_args=default_args,
    description='Extract CSV and JSON files, transform data, and load into Postgres',
    schedule_interval='@once'
)

# Extract CSV files
cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
def extract_csv_files():
    df1 = pd.read_csv('/Users/sanvi/Documents/final project/airflow-fp/dags/data/precipitation.csv')
    df2 = pd.read_csv('/Users/sanvi/Documents/final project/airflow-fp/dags/data/temperature.csv')
    return df1, df2

# Extract JSON files
def extract_json_files():
    data = []
    for i in range(1, 6):
        with open(f'/Users/sanvi/Documents/final project/airflow-fp/data/json/yelp_academic_dataset_business1.json') as f:
            json_data = json.load(f)
            data.append(json_data)
    return data

# Transform data
def transform_data():
    df1, df2 = extract_csv_files()
    json_data = extract_json_files()

    # Perform transformations on CSV files
    df1['date'] = pd.to_datetime(df1['date'], format='%Y-%m-%d')
    df2['date'] = pd.to_datetime(df2['date'], format='%Y-%m-%d')

    # Perform transformations on JSON data
    for data in json_data:
        for item in data:
            item['date'] = datetime.strptime(item['date'], '%Y-%m-%d')

    return df1, df2, json_data

# Load data into Postgres
def load_data():
    conn = psycopg2.connect(
        host="localhost",
        database="airflow",
        user="airflow",
        password="airflow"
    )
    cur = conn.cursor()

    # Extract and transform data
    df1, df2, json_data = transform_data()

    # Load CSV data into Postgres
    df1.to_sql('table1', con=conn, if_exists='replace', index=False)
    df2.to_sql('table2', con=conn, if_exists='replace', index=False)

    # Load JSON data into Postgres
    for data in json_data:
        for item in data:
            cur.execute("""
                INSERT INTO table3 (date, value1, value2)
                VALUES (%s, %s, %s);
            """, (item['date'], item['value1'], item['value2']))
    
    # Commit changes and close connection
    conn.commit()
    cur.close()
    conn.close()

# Define DAG tasks
extract_csv_task = PythonOperator(
    task_id='extract_csv_files',
    python_callable=extract_csv_files,
    dag=dag
)

extract_json_task = PythonOperator(
    task_id='extract_json_files',
    python_callable=extract_json_files,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag
)

# Set task dependencies
extract_csv_task >> transform_task >> load_task
