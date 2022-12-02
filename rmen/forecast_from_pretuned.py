import os
from dotenv import load_dotenv
load_dotenv()
from rmen.model import Model
from rmen.forecast import Forecast
from datetime import date
import pickle
from dateutil.relativedelta import relativedelta
storage_path = os.path.join(os.getenv("project_dir"), "assets", "storage", "rmedb_storage.db")


def _init_from_tuned_(tuned_forecast):
    
    tuned_model = Model(method= tuned_forecast.model.method,
                        name = tuned_forecast.model.name,
                        params = tuned_forecast.model.estimator[1].best_params_,
                        best_estimator = tuned_forecast.model.estimator[1].best_estimator_)
    forecast = Forecast(variable = tuned_forecast.variable
           , model = tuned_model
           , predictor = tuned_forecast.predictor
           , horizon = tuned_forecast.horizon
           , name = tuned_forecast.name
           , train_start_dt = "2008-01-01"
           , test_start_dt = (date.today() - relativedelta(years=2)).strftime(format = "%Y-%m-%d")
           , test_end_dt = date.today().strftime(format = "%Y-%m-%d")
            )
    return forecast

def forecast_pipeline_pretuned():
    tuned_path = os.path.join(os.getenv("project_dir"), "assets", "model", 'tuned')
    final_path = os.path.join(os.getenv("project_dir"),
                         "assets",
                         "model",
                        "final",
                         f"{date.today().strftime(format = '%Y-%m-%d')}.pickle")
    
    forecast_list = []
    for fi in os.listdir(tuned_path):
        with open(os.path.join(tuned_path, fi), "rb") as f:
            tuned_forecast = pickle.load(f)
        forecast = _init_from_tuned_(tuned_forecast)
        forecast.collect_data()
        forecast.cut_data()
        forecast.split_data()
        forecast.fit_in_loop()
        forecast.get_metric()
        forecast_list.append(forecast)

    with open(final_path, "wb") as f:
        pickle.dump(forecast_list, f)
if __name__ == '__main__':
    forecast_pipeline_pretuned()