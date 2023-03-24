
import os
import psycopg2
import pandas as pd
import sqlalchemy

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)



df = pd.read_json("airflow-fp/data/json/yelp_academic_dataset_review3.json", lines=True)
# print(df.isna().sum())
# df_drop = df.dropna()
# print(df_drop.isna().sum())

# df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

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
    cur.execute("DROP TABLE IF EXISTS raw_layer.yelp_review")

    sql_create = """
        CREATE TABLE raw_layer.yelp_review(
            review_id TEXT PRIMARY KEY,
            user_id TEXT,
            business_id TEXT,
            stars float,
            useful int,
            funny int,
            cool int,
            text TEXT,
            date date
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
    INSERT INTO raw_layer.yelp_review(
        review_id,
        user_id,
        business_id,
        stars,
        useful,
        funny,
        cool,
        text,
        date
    ) VALUES %s 
    """

    psycopg2.extras.execute_values(cur, sql_insert, df.values)
    # df.to_sql('yelp_business', schema='raw_layer', con=db, dtype={'attributes': sqlalchemy.types.JSON, 'hours': sqlalchemy.types.JSON}, index=False, if_exists='replace')
    
    conn.commit()
    conn.close()

    cur.close()

    print("Insert to table success")

except Exception as e:
    print(e)