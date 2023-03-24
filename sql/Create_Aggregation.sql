CREATE TABLE IF NOT EXISTS agg_ReviewDay (
    date date, 
    stars char,
    count_review int4,
    min int4,
    max int4,
    normal_min int4, 
    normal_max int4,
    precipitation float8,
    precipitation_normal float8)