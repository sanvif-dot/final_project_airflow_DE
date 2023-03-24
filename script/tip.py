
import os
import psycopg2
import pandas as pd
import sqlalchemy

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)



df = pd.read_json("airflow-fp/data/json/yelp_academic_dataset_tip4.json", lines=True)
# print(df.isna().sum())
# print(df[:35])
# print(df.dtypes)
# print(df['hours'])
# df_drop = df.dropna()
# print(df_drop.isna().sum())

database = "postgres"
user = "airflow"
passwd = "airflow"
hostname = "localhost"
port = "5432"

conn_string = 'postgresql://airflow:airflow@localhost:5432/postgres'
db = sqlalchemy.create_engine(conn_string)
conn_engine = db.connect()

try:
    conn = psycopg2.connect(conn_string)
    
    print("Connection success")

except Exception as e:
    print(e)

cur = conn.cursor()

try:
    cur.execute("DROP TABLE IF EXISTS raw_layer.yelp_tip")

    sql_create = """
        CREATE TABLE raw_layer.yelp_tip(
            user_id TEXT,
            business_id TEXT,
            text_tip TEXT,
            date date,
            compliment_count int
        );
        """

    cur.execute(sql_create)

    conn.commit()
    # conn.close()

    print("Create table success")

except Exception as e:
    print(e)

try:
    sql_insert = f"""
    INSERT INTO raw_layer.yelp_tip(
        user_id,
        business_id,
        text_tip,
        date,
        compliment_count
    ) VALUES %s 
    """

    # df.to_sql('yelp_tip', schema='raw_layer', con=db, index=False, if_exists='replace', method='multi')
    psycopg2.extras.execute_values(cur, sql_insert, df.values)
    
    conn.commit()
    conn.close()

    cur.close()

    print("Insert to table success")

except Exception as e:
    print(e)