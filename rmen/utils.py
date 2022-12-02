import os
from typing import Literal
from dotenv import load_dotenv
load_dotenv()
import sqlite3 as sl
from matplotlib.dates import num2date
from datetime import date
import pandas as pd

class IncorrectPredictorError(Exception):
    pass
class IncorrectStartDtError(Exception):
    pass
class IncorrectDtError(Exception):
    pass

interim_storage_path = os.path.join(os.getenv("project_dir"), "assets", "storage", "rmedb_storage.db")

# def interim_storage_connect():
#     path = get_interim_storage_path()
#     return sl.connect(path, timeout=0.01)

def check_forecast_args(fun):
    def wrapper(*args,**kwargs):
        with sl.connect(interim_storage_path) as conn:
            cursor = conn.cursor()
            if ("train_start_dt"  in kwargs) and ("test_start_dt" in kwargs) and ("test_end_dt" in kwargs):
                if not (kwargs["train_start_dt"] < kwargs["test_start_dt"] < kwargs["test_end_dt"]):
                    raise IncorrectDtError("Dates are not compatible.")
            if "predictor" in kwargs:
                cursor.execute(f"SELECT ticker FROM VARIABLE")
                tickers  = (i[0] for i in cursor.fetchall())
                if not set(kwargs["predictor"].keys()).issubset(set(tickers)):
                    diff = set(kwargs["predictor"]).difference(set(tickers))
                    raise IncorrectPredictorError(f'These predictors are not available in raw data: {diff}')
            if  ("variable" in kwargs) and ("train_start_dt" in kwargs):
                if kwargs["train_start_dt"] < kwargs["variable"].start_dt:
                    raise IncorrectDtError(f'Train start date is {kwargs["train_start_dt"]}')
            
        return fun(*args,**kwargs)
    return wrapper
def check_data(fun):
    def wrapper(*args,**kwargs):
        return fun(*args,**kwargs)
    return wrapper
def check_variable(fun):
    def wrapper(*args,**kwargs):
        return fun(*args,**kwargs)
    return wrapper


def get_xid(data):
    return data.columns!="target__"

def formatter(x, pos):
    return f"{x:.1%}"


def quarter_formatter( x, pos):
    quarters = ["I", "II", "III", "IV"]
    dt = num2date(x)
    quarter = quarters[int(dt.month/4)]

    return f"{dt.year}-{quarter}"

def generate_date_series(f:Literal["q", "m"]):
    
    if f=="q":
        return pd.date_range(pd.to_datetime("2000-01-01"), 
                   pd.to_datetime(date.today()) + pd.offsets.QuarterBegin(1), freq='QS').strftime(date_format = "%Y-%m-%d")
    else:
        return pd.date_range(pd.to_datetime("2000-01-01"), 
                   pd.to_datetime(date.today()) + pd.offsets.MonthBegin(1), freq='MS').strftime(date_format = "%Y-%m-%d")
