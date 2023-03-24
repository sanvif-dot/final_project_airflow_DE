# Import airflow modules
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# Import modules
from datetime import datetime,date
import pandas as pd
import os
from sqlalchemy import create_engine

# Arguments
default_args = {
    'owner':'Pedrosa',
    'start_date':datetime(2023,2,1)
}

# Extract data from data/ to data/csv/{today-date}
def _extract_csv_file():
    today = date.today()

    df = pd.read_csv("./dags/data/order_details.csv", header=0, delimiter=",")

    if not os.path.exists("./dags/data/csv/{}".format(today)):
        os.mkdir("./dags/data/csv/{}".format(today))
    else:
        pass

    df.to_csv(os.path.abspath("./dags/data/csv/{}/order_details.csv".format(today)))

# Extract data from database to data/postgres/{today-date}
def _extract_database_tables():
    today = date.today()

    if not os.path.exists("./dags/data/postgres/{}".format(today)):
        os.mkdir("./dags/data/postgres/{}".format(today))

    try:
        engine = create_engine('postgresql://airflow:airflow@postgres:5432/postgres')

        tables = ['categories', 'customer_customer_demo', 'customer_demographics', 'customers', 'employee_territories', 'employees', 'orders','products','region', 'shippers', 'suppliers', 'territories', 'us_states']

        for table in tables:
            df = pd.read_sql_query("select * from {};".format(table),con=engine)

            df.to_csv("./dags/data/postgres/{}/{}.csv".format(today, table))

    except Exception as e:
        print("Erro:", e)

# Load data from data/csv/{today-date} and data/postgres/{today-date} to database
def _load_to_database():
    today = date.today()

    try:
        engine = create_engine('postgresql://airflow:airflow@postgres:5432/postgres')
        # engine = create_engine('postgresql+psycopg2://postgres:postgres@host.docker.internal/southwind')

        df_csv = pd.read_csv("./dags/data/csv/{}/order_details.csv".format(today), header=0, delimiter=",")

        df_csv.to_sql("order_details", con=engine, if_exists="replace", index=False)

        df_table = pd.read_csv("./dags/data/postgres/{}/orders.csv".format(today), header=0, delimiter=',')

        df_table.to_sql("orders", con=engine, if_exists="replace", index=False)

    except Exception as e:
        print("Erro:", e)

#DAG
with DAG(
    dag_id="batch_pipeline",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    template_searchpath="/opt/airflow/plugins"
) as dag:
    
    extract_csv_file = PythonOperator(
        task_id="extract_csv_file",
        python_callable=_extract_csv_file
    )

    extract_database_tables = PythonOperator(
        task_id="extract_database_tables",
        python_callable=_extract_database_tables
    )

    # Create table in the output database
    create_tables = PostgresOperator(
        task_id="create_tables",
        postgres_conn_id="conn_postgres",
        sql= "create_tables.sql"
    )

    load_to_database = PythonOperator(
        task_id="load_to_database",
        python_callable=_load_to_database
    )

# DAG tasks sequence
    extract_csv_file >> extract_database_tables >> create_tables >> load_to_database