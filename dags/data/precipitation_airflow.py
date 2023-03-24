
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.postgres_operator import PostgresOperator

from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 21),
  
}

dag = DAG(
    'precipitation',
    default_args=default_args,
    description='Example DAG for extracting, transforming, and loading CSV data into PostgreSQL',
    schedule_interval=timedelta(days=1)
)

def extract_transform_csv():
    df = pd.read_csv('/Users/sanvi/Documents/final project/airflow-fp/dags/data/precipitation.csv')
    df['date_column'] = pd.to_datetime(df['date_column'].str.replace('T', '0'), format='%Y-%m-%d %H:%M:%S.%f')
    df.to_csv('/Users/sanvi/Documents/final project/airflow-fp/dags/data/file.csv', index=False)

def load_csv_to_postgres():
    engine = create_engine('postgresql://airflow:airflow@localhost:5432/airflow')
    conn = engine.connect()
    conn.execute('CREATE TABLE IF NOT EXISTS table_name (column1 datatype1, column2 datatype2, ...)')
    df = pd.read_csv('/Users/sanvi/Documents/final project/airflow-fp/dags/data/file.csv')
    df.to_sql('table_name', con=engine, if_exists='append', index=False)
    conn.close()

with dag:
    extract_csv_task = PythonOperator(
        task_id='extract_csv',
        python_callable=extract_transform_csv
    )

    load_to_postgres_task = PythonOperator(
        task_id='load_to_postgres',
        python_callable=load_csv_to_postgres
    )

    create_postgres_table = PostgresOperator(
        task_id='create_table',
        sql="""
        CREATE TABLE IF NOT EXISTS table_name (
            column1 datatype1,
            column2 datatype2,
            ...
        )
        """,
        postgres_conn_id='postgres_default'
    )

    extract_csv_task >> load_to_postgres_task >> create_postgres_table

