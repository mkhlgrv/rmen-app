from dotenv import load_dotenv
load_dotenv()
from typing import Literal, Optional
from sklearn.linear_model import ElasticNetCV
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from rmen.logger import logger, sklearn_verbose
import os

class Model:
    def __init__(self
                 , method : Literal["ElasticNet","RandomForest","XGB"]
                 , name : dict
                 , params : dict
                 , desc : Optional[str] = None
                 , best_estimator = None):
        self.method = method
        self.name = name
        self.params = params
        self.desc = desc
        self.get_estimator(best_estimator)
    def get_estimator(self, best_estimator):
        if best_estimator is None:
            if self.method == "ElasticNet":
                regressor = ElasticNetCV()
            elif self.method == "RandomForest":
                regressor = RandomForestRegressor()
            elif self.method == "XGB":
                regressor = XGBRegressor()

            regressor = RandomizedSearchCV(estimator = regressor,
                               param_distributions = self.params,
                               n_iter = 500,
                               cv = 3,
                               verbose=sklearn_verbose,
                               random_state=10)
        else:
            regressor = best_estimator

        self.estimator = Pipeline([('scaler', StandardScaler()),
                          ('regressor', regressor)])