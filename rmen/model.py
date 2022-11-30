from dotenv import load_dotenv
load_dotenv()
from typing import Literal, Optional
from sklearn.linear_model import ElasticNetCV
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RandomizedSearchCV

class Model:
    def __init__(self
                 , method : Literal["ElasticNet","RandomForest","XGB"]
                 , name : dict
                 , params : dict
                 , desc : Optional[str] = None):
        self.method = method
        self.name = name
        self.params = params
        self.desc = desc
        self.get_estimator()
    def get_estimator(self):
        if self.method == "ElasticNet":
            regressor = ElasticNetCV()
        elif self.method == "RandomForest":
            regressor = RandomForestRegressor()
        elif self.method == "XGB":
            regressor = XGBRegressor()
        regressor_cv = RandomizedSearchCV(estimator = regressor,
                           param_distributions = self.params,
                           n_iter = 500,
                           cv = 3,
                           verbose=0,
                           random_state=10)

        self.estimator = Pipeline([('scaler', StandardScaler()),
                          ('regressor', regressor_cv)])