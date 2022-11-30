from dotenv import load_dotenv
load_dotenv()
import pandas as pd
from typing import Optional
import numpy as np
from sklearn import metrics
import sqlite3 as sl
from rmen.utils import check_forecast_args, check_data, get_xid
from rmen.utils import interim_storage_path as storage_path
from rmen.variable import Variable
from rmen.model import Model

truncate_predictor = "DELETE FROM PREDICTOR;"
insert_predictor = """INSERT INTO PREDICTOR
                  ('ticker', 'lag') 
                  VALUES (?, ?);"""
select_predictor = """
        WITH variable_frequency AS 
(
SELECT
    ticker
    , deseason
    , CASE
        WHEN freq = 'q' THEN 4
        WHEN freq = 'm' THEN 12
        WHEN freq = 'w' THEN 52
        ELSE 255
    END AS frequency
FROM
    variable)
,
deseason_value AS 
(
SELECT
    val.ticker
    , val.dt
    , var.frequency
    , CASE
        WHEN 
            var.deseason = 'diff' 
        THEN
            val.value - lag(val.value
        , var.frequency) 
                OVER (PARTITION BY val.ticker
    ORDER BY
        val.dt)
        WHEN 
            var.deseason = 'logdiff' 
        THEN  
            val.value / (lag(val.value
        , var.frequency) 
                OVER (PARTITION BY val.ticker
    ORDER BY
        val.dt)) -1
        ELSE 
            val.value
    END AS value
FROM 
    value val
INNER JOIN 
    variable_frequency var
ON 
    val.ticker = var.ticker)
,
total_shift AS (
SELECT
    pred.ticker
    , pred.lag
    , pred.lag + ps.shift AS shift
FROM
    PREDICTOR pred
INNER JOIN
    publication_shift ps
ON
    pred.ticker = ps.ticker)
,
target_min_dt AS (
SELECT
    min(dt) AS min_dt
FROM
    deseason_value
WHERE
    ticker = '{ticker}'
    AND value IS NOT NULL
)
, 
target AS (
-- отдельно добавляем нужные даты
SELECT 
    'target__' AS ticker
    , dr.dt
    , coalesce(dv.value, -1000000)
FROM
date_range dr 
LEFT JOIN 
    (
    SELECT
        dt
        , value
    FROM 
        deseason_value
    WHERE 
        ticker = '{ticker}') dv
ON
    date(dr.dt) = date(dv.dt)
INNER JOIN target_min_dt tmd
ON 1 = 1
WHERE
    dr.freq = '{freq}'
    AND date(dr.dt) >= date(tmd.min_dt)
    AND date(dr.dt) <= date('now', (({horizon} * 12/{frequency}) ||' month'))
)
, 
deseasoned_shifted AS (
SELECT
    ts.ticker || '__' || ts.lag AS ticker
    , date(val.dt, 'start of month',
        (CASE WHEN sign(ts.shift * 12 / val.frequency +
        ({horizon})* 12 /({frequency}))= 1 THEN '+' ELSE '-' END) 
        || abs(ts.shift * 12 / val.frequency +
        ({horizon})* 12 /({frequency}))
        || ' month') AS dt
    , val.value
FROM
    total_shift ts
INNER JOIN
    deseason_value val
ON
    val.ticker = ts.ticker
UNION ALL
SELECT
    *
FROM
    target)
SELECT
    ticker,
    dt, 
    value
FROM
    deseasoned_shifted;
"""



class Forecast:
    @check_forecast_args
    def __init__(self
                 , *
                 , variable:Variable
                 , model:Model
                 , predictor:dict
                 , horizon:int
                 , train_start_dt:str
                 , test_start_dt:str
                 , test_end_dt:str
                 , name: Optional[dict] = None
                 , desc: Optional[str] = None):
        self.variable = variable
        self.model = model
        self.method = model.method
        self.params = model.params
        self.predictor = predictor
        self.horizon = horizon
        self.train_start_dt = train_start_dt
        self.test_start_dt = test_start_dt
        self.test_end_dt = test_end_dt
        self.name = name if name is not None else f"{variable.name['rus']} / {model.name['rus']}"
        self.desc = desc

    def collect_data(self):
        ticker_lag = [(key, i) for key, item in self.predictor.items() for i in item]
        with sl.connect(storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute(truncate_predictor)
            cursor.executemany(insert_predictor, ticker_lag)
            data = pd.read_sql(select_predictor.format(ticker = self.variable.ticker,
                                                       horizon = self.horizon,
                                                      freq = self.variable.freq,
                                                      frequency = 4 if self.variable.freq == "q" else 12), conn)
            data = data.pivot(values = "value", index = "dt", columns = "ticker")

            data = data[(~data["target__"].isna())]
            
            data["target__"] = np.where(data["target__"] <-100000, np.NaN,data["target__"])
            
            self.data = data



    def cut_data(self):

        self.data = self.data[(self.data.index >= self.train_start_dt) & (self.data.index <=  self.test_end_dt)]
        self.data = self.data.loc[:,(~self.data.isna().any())|(~get_xid(self.data))]

    @check_data
    def split_data(self):

        self.is_initial_window = self.data.index <  self.test_start_dt

        self.X, self.y = self.data.loc[:,get_xid(self.data)].to_numpy(), \
                         self.data.loc[:,~get_xid(self.data)].to_numpy().ravel()

        self.y_predict = np.empty_like(self.y)

        self.y_predict[:] = np.nan



    def fit_by_step(self, step):
        last_notna = sum(~np.isnan(self.y))
        train_bound = min(step, last_notna)
        
        X_train, y_train = self.X[:train_bound], self.y[:train_bound]
        X_test = self.X[[step]]
        self.model.estimator.fit(X_train, y_train)
        self.y_predict[step] = self.model.estimator.predict(X_test)


    def fit_in_loop(self):
        start, stop = sum(self.is_initial_window), len(self.data)

        for step in range(start, stop):
            self.fit_by_step(step)

    def get_metric(self):
        is_consistent = ~(np.isnan(self.y) | np.isnan(self.y_predict))
        y = self.y[is_consistent], self.y_predict[is_consistent]
        self.r2 = metrics.r2_score(*y)
        self.max_error = metrics.max_error(*y)
        self.rmse = np.sqrt(metrics.mean_squared_error(*y))
        self.mae = metrics.median_absolute_error(*y)