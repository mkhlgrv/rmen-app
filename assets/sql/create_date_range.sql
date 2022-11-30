CREATE VIEW IF NOT EXISTS date_range AS
WITH 
 RECURSIVE dates_q(freq,dt) AS (
   VALUES('q','2000-01-01')
   UNION ALL
   SELECT 'q' as freq, date(dt, '+3 month') as dt
   FROM dates_q
   WHERE date(dt, '+3 month') < date('now', '+12 month')
 )
,
dates_m(freq,dt) AS (
  VALUES('m','2000-01-01')
  UNION ALL
  SELECT 'm' as freq, date(dt, '+1 month') as dt
  FROM dates_m
  WHERE date(dt, '+1 month') < date('now', '+12 month')
)
SELECT  freq, dt FROM dates_m
UNION ALL 
SELECT  freq, dt FROM dates_q
;