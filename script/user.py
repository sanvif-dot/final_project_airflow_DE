
import os
import psycopg2
import pandas as pd
import sqlalchemy

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)



df = pd.read_json("airflow-fp/data/json/yelp_academic_dataset_user5.json", lines=True)
# print(df.isna().sum())
# df_drop = df.dropna()
# print(df_drop.isna().sum())
# drop unnecessary columns because my PC can't handle large file while processing it. 
df_drop = df.drop([
        'elite',
        'friends',
        'compliment_hot',
        'compliment_more',
        'compliment_profile',
        'compliment_cute',
        'compliment_list',
        'compliment_note',
        'compliment_plain',
        'compliment_cool',
        'compliment_funny',
        'compliment_writer',
        'compliment_photos'], axis=1)
# print(df)
# print(data)
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
    cur.execute("DROP TABLE IF EXISTS raw_layer.yelp_user")

    sql_create = """
        CREATE TABLE raw_layer.yelp_user(
            user_id TEXT PRIMARY KEY,
            name TEXT,
            review_count int,
            yelping_since date,
            useful int,
            funny int,
            cool int,
            fans int,
            average_stars float
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
    INSERT INTO raw_layer.yelp_user(
        user_id,
        name,
        review_count,
        yelping_since,
        useful,
        funny,
        cool,
        fans,
        average_stars
    ) VALUES %s
    """

    # using execute values because it is faster and not eating as much resources. to sql is better but it is slower without multi method and eat so much resource
    # df.to_sql('yelp_user', schema='raw_layer', con=db, index=False, if_exists='replace', method='multi')
    psycopg2.extras.execute_values(cur, sql_insert, df_drop.values)
    
    conn.commit()
    conn.close()

    cur.close()

    print("Insert to table success")

except Exception as e:
    print(e)