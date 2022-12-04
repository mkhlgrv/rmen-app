from dotenv import load_dotenv
load_dotenv()
from typing import Literal, Optional
from sklearn.linear_model import ElasticNetCV, LassoCV
from sklearn.ensemble import RandomForestRegressor
#from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV, ParameterGrid
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
        self.best_estimator = best_estimator
        self._get_niter_()
        self._get_estimator_()
    def _get_niter_(self):
        if self.best_estimator is None:
            param_grid_len = len(list(ParameterGrid(self.params)))
            self.n_iter = min(500, param_grid_len)
        else:
            self.n_iter = 1

    def _get_estimator_(self):
        if self.best_estimator is not None:
            regressor = self.best_estimator

        else:
            if self.method == "ElasticNet":
                regressor = ElasticNetCV()
            elif self.method == "Lasso":
                regressor = LassoCV()
            elif self.method == "RandomForest":
                regressor = RandomForestRegressor()
            elif self.method == "XGB":
                regressor = XGBRegressor()

            regressor = RandomizedSearchCV(estimator = regressor,
                               param_distributions = self.params,
                               n_iter = self.n_iter,
                               cv = 5,
                               verbose=sklearn_verbose,
                               random_state=10)
            

        self.estimator = Pipeline([('scaler', StandardScaler()),
                          ('regressor', regressor)])
