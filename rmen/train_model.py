import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, datestr2num, num2date
from rmen.variable import Variable
from rmen.model import Model
from rmen.forecast import Forecast
import json
import pandas as pd
import sqlite3 as sl
from rmen.utils import interim_storage_path as storage_path
from datetime import date
import asyncio
import time
import pickle
from pathlib import Path

storage_path = os.path.join(os.getenv("project_dir"), "assets", "storage", "rmedb_storage.db")
save_dir = os.path.join(os.getenv("project_dir"), "assets", "model", str(date.today()))
Path(save_dir).mkdir(exist_ok=True)



targets = ["gdp_real", "cons_real", "export_real", "invest_real", "cpi"]
variables = [Variable(target) for target in targets]


methods = [Model(method = "ElasticNet", name = {"rus":"EN"},
                params = {"l1_ratio":[i for i in np.arange(0.1,1.,.2)],
                          "selection":["random"]}),
           Model(method = "ElasticNet", name = {"rus":"LASSO"},
                 params = {"l1_ratio":[0.95],
                           "selection":["random"]}),
           Model(method = "ElasticNet", name = {"rus":"Ridge"},
                 params = {"l1_ratio":[0.05],
                           "selection":["random"]}),
           Model(method= "RandomForest", name = {"rus":"RF/N=100"},
                 params={"n_estimators":[100],
                         "criterion":["squared_error"],
                         "max_depth" : [5,10,20],
                         "min_samples_split":[2,3,5],
                         "min_samples_leaf":[1,2],
                         "max_features":[0.3,"log2",1],
                         "bootstrap":[True, False]
                         }),
          Model(method= "RandomForest", name = {"rus":"RF/N=500"},
                 params={"n_estimators":[500],
                         "criterion":["squared_error"],
                         "max_depth" : [5,10,20],
                         "min_samples_split":[2,3,5],
                         "min_samples_leaf":[1,2],
                         "max_features":[0.3,"log2",1],
                         "bootstrap":[True, False]
                         })
#            ,Model(method= "XGB", name = {"rus":"XGB/N=100"},
#                  params={"n_estimators":[100],
#                          "criterion":["squared_error"],
#                          "max_depth" : [5,10,20],
#                          "max_leaves":[0,5,10],
#                          "grow_policy":[0,1],
#                          "learning_rate":[0.2,0.3,0.5],
#                          "booster":["gbtree", "gblinear"],
#                          "subsample":[0.5,1],
#                          "colsample_bytree":[0.3,0.5,1],
#                          "reg_alpha":[0.5],
#                          "tree_method":["approx","hist"],
#                          })
          ]


with open(os.path.join(os.getenv("project_dir"), "assets", "json", "predictor_rosstat.json")) as f:
    predictor_rosstat = json.load(f)
with open(os.path.join(os.getenv("project_dir"), "assets", "json", "predictor_all.json")) as f:
    predictor_all = json.load(f)
predictors = [{"name":"Росстат", "predictor":predictor_rosstat},
             {"name":"Все", "predictor":predictor_all}]



def initialize_in_loop():
    forecast_list = []
    for variable in variables:
        for method in methods[3:5]:
            for predictor in predictors:
                for horizon in [-1, 0]:
                    forecast_list.append(Forecast(variable = variable
                                       , model = method
                                       , predictor = predictor["predictor"]
                                       , horizon = horizon
                                       , name = f"{method.name['rus']} / {predictor['name']}"
                                       , train_start_dt = "2008-01-01"
                                       , test_start_dt = "2015-01-01"
                                       , test_end_dt = date.today().strftime(format = '%Y-%m-%d')
                                                 ))
    return forecast_list

def forecast_pipeline(forecast:Forecast, i:int, save_dir:str, debug:bool=False):
    forecast.collect_data()
    forecast.cut_data()
    forecast.split_data()
    forecast.fit_in_loop()
    forecast.get_metric()
    if not debug:
        forecast.model = None          
    with open(os.path.join(save_dir, f"{i}.pickle"), "wb") as f:
        pickle.dump(forecast, f)
        
        
forecast_list = initialize_in_loop()
[forecast_pipeline(forecast, i, save_dir, ) for i, forecast in enumerate(forecast_list)]

forecast_list_out = []
for fi in os.listdir(save_dir):
    with open(os.path.join(save_dir, fi), "rb") as f:
        forecast_list_out.append(pickle.load(f))
with open(os.path.join(os.getenv("project_dir"), "assets", "model", f"{str(date.today())}.pickle"), "wb") as f:
    pickle.dump(forecast_list_out, f)