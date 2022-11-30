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
import os
import json
export_dir = os.path.join(os.getenv("project_dir"), "assets", "json")



# select ticker from VARIABLE;

with sl.connect(storage_path) as conn, open(os.path.join(export_dir, "predictor_rosstat.json"), 'w', encoding='utf-8') as f:
    cursor = conn.cursor()
    tickers = cursor.execute("SELECT ticker FROM variable where source = 'rosstat';").fetchall()
    ticker_dict = {ticker:[0,1] for ticker, in tickers}
    f.write(json.dumps(ticker_dict, ensure_ascii=False))
    
    
with sl.connect(storage_path) as conn, open(os.path.join(export_dir, "predictor_all.json"), 'w', encoding='utf-8') as f:
    cursor = conn.cursor()
    tickers = cursor.execute("SELECT ticker FROM variable where freq != 'd' and freq != 'w';").fetchall()
    ticker_dict = {ticker:[0,1] for ticker, in tickers}
    f.write(json.dumps(ticker_dict, ensure_ascii=False))
