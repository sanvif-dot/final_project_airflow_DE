INSERT INTO agg_ReviewDay(date, stars, count_review, min, max, normal_min, normal_max,precipitation,precipitation_normal)
        SELECT review.date::date, 
               review.stars::char,
               count_review, 
               min, 
               max, 
               normal_min, 
               normal_max,
               precipitation::float,
               precipitation_normal
        FROM (SELECT fact_review.date::date,
                     fact_review.stars::char,
                     COUNT(review_id) AS count_review
              FROM fact_review 
              GROUP BY fact_review.date, fact_review.stars::char) AS review
        LEFT JOIN climate_temperature
        ON DATE(review.date) = DATE(climate_temperature.date)
        LEFT JOIN climate_precipitation 
        ON DATE(review.date) = DATE(climate_precipitation.date)