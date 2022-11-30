from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, datestr2num, num2date
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from matplotlib.colors import to_rgb
from typing import List
from rmen.variable import Variable
from rmen.forecast import Forecast
from rmen.utils import check_variable, quarter_formatter, formatter

class Statistic():
    @check_variable
    def __init__(self, variable:Variable, forecast:List[Forecast], left_bound:str="2015-01-01"):
        self.variable = variable
        self.forecast = forecast
        self.left_bound = left_bound
        if variable.freq=="q":

            self.date_formatter = quarter_formatter
        else:
            self.date_formatter = DateFormatter("%Y-%m")
    def show_metric(self):
        metric = []
        for f in self.forecast:
            metric.append((f.name, f.r2, f.rmse, f.max_error, f.mae))
        return metric
    def to_file(self, file_type:str):
        if file_type == "csv":
            out = []

            for f in self.forecast:
                for dt, y, y_predict in zip(f.data.index, f.y, f.y_predict):
                    if not np.isnan(y_predict):
                        out.append((dt, f.name, f.variable.ticker, y, y_predict))
            df = pd.DataFrame(out, columns = ["date", "name", "ticker", "true", "predict"])
            return df

        if file_type == "json":
            out = []
            for f in self.forecast:
                out.append({"name":f.name
                               , "data":f.data.to_dict(orient='dict')
                               , "model": {"method":f.model.method, "params" :f.model.params}
                               , "horizon": f.horizon
                               , "test_start_dt":f.test_start_dt
                               , "y":f.y.tolist()
                               , "y_predict":f.y_predict.tolist()
                               , "metrics":{"r2":f.r2, "rmse":f.rmse, "max_error":f.max_error, "MAE":f.mae}
                            })
            return  out
    def plot(self, ci:bool):


        fig, ax = plt.subplots(1,2, figsize = (14,8))
        ax[0].plot(datestr2num(self.forecast[0].data.index), self.forecast[0].y, color="black", alpha =0.5, label = "Факт")
        for f in self.forecast:
            l = ax[0].plot(datestr2num(f.data.index), f.y_predict, label = f.name)
            ax[0].scatter(datestr2num(f.data.index), f.y_predict)
            if ci:
                ax[0].fill_between(datestr2num(f.data.index), f.y_predict+f.rmse,f.y_predict-f.rmse
                                   , alpha=0.2, color = l[0].get_color())

            ax[1].bar(f.name, f.y_predict[-1],yerr=f.rmse, capsize=10, alpha=0.5, error_kw ={"alpha":0.5})
            ax[1].text(f.name, f.y_predict[-1] + np.sign(f.y_predict[-1])*0.0008
                       , f"{f.y_predict[-1]:.2%}",va='center_baseline', ha = "center")

        ax[0].xaxis.set_major_formatter(self.date_formatter)
        ax[0].legend()
        ax[0].set_xlim(left=self.left_bound)
        ax[0].grid(True)
        ax[1].grid(True)
        ax[0].yaxis.set_major_formatter(formatter)
        ax[1].yaxis.set_major_formatter(formatter)
        ax[0].set_xlabel("Дата")
        ax[0].set_ylabel("Изменение, % год к году")
        ax[0].set_title("Исторический прогноз")

        ax[1].set_xlabel("Модель")
        ax[1].set_title("Текущий прогноз")


        return fig, ax
    def plotly(self, show_ci):


        def quarter_formatter( x):
            dt = num2date(x)
            if self.variable.freq=="q":
                quarters = ["I", "II", "III", "IV"]

                quarter = quarters[int(dt.month/3)]

                return f"{dt.year}-{quarter}"
            else:
                return f"{dt.year}-{dt.month}"

        quarter_formatter_v = np.vectorize(quarter_formatter)

        fig = make_subplots(rows=1, cols=2
                            , subplot_titles=("Исторический прогноз", f"Текущий прогноз ( {quarter_formatter_v(datestr2num(self.forecast[0].data.index[-1]))})"))

        fig.add_trace(
            go.Scatter(x=quarter_formatter_v(datestr2num(self.forecast[0].data.index[self.forecast[0].data.index>=self.left_bound]))
                       , y=self.forecast[0].y[self.forecast[0].data.index>=self.left_bound]*100
                       , name="Факт"
                       )
            , row=1, col=1
        )
        fig.data[-1].line.color = "black"
        palette = px.colors.qualitative.Dark24


        forecast_order = np.argsort(np.array([f.y_predict[-1] for f in self.forecast]))
        forecast_sorted = [self.forecast[i] for i in forecast_order]
        for color, f in zip(palette, forecast_sorted):
            fig.add_trace(
                go.Scatter(x=quarter_formatter_v(datestr2num(f.data.index[f.data.index>=self.left_bound]))
                           , y=f.y_predict[f.data.index>=self.left_bound]*100
                           , name= f.name
                           )
                , row=1, col=1
            )
            fig.data[-1].line.color = color

            fillcolor = (*to_rgb(color), 0.2)

            fillcolor = f"rgba({fillcolor[0]},{fillcolor[1]},{fillcolor[2]},{fillcolor[3]})"
            if show_ci:
                fig.add_traces([go.Scatter(x = quarter_formatter_v(datestr2num(f.data.index[f.data.index>=self.left_bound]))
                                           , y = (f.y_predict[f.data.index>=self.left_bound]+f.rmse)*100,
                                           mode = 'lines', line_color = fillcolor,
                                           showlegend = False),
                                go.Scatter(x = quarter_formatter_v(datestr2num(f.data.index[f.data.index>=self.left_bound]))
                                           , y = (f.y_predict[f.data.index>=self.left_bound]-f.rmse)*100,
                                           mode = 'lines', line_color = fillcolor,
                                           showlegend = False,
                                           fill='tonexty', fillcolor = fillcolor)], rows=1, cols=1)


            fig.add_trace(
                go.Bar(x=[f.name], y = [f.y_predict[-1]*100], name= f.name, marker_color=color
                       , showlegend =False)
                , row=1, col=2
            )

        fig.update_layout(xaxis_title="Дата",
#                           xaxis=dict(
#                             rangeselector=dict(
#                                 buttons=list([
#                                     dict(count=1,
#                                          label="1m",
#                                          step="month",
#                                          stepmode="backward"),
#                                     dict(count=6,
#                                          label="6m",
#                                          step="month",
#                                          stepmode="backward"),
#                                     dict(count=1,
#                                          label="YTD",
#                                          step="year",
#                                          stepmode="todate"),
#                                     dict(count=1,
#                                          label="1y",
#                                          step="year",
#                                          stepmode="backward"),
#                                     dict(step="all")
#                                 ])
#                             ),
#                             rangeslider=dict(
#                                 visible=True
#                             ),
#                             type="date"
#                         ),
                          width=1500, height=800,
                          title={
                              'text': self.forecast[0].variable.name["rus"]
                              , 'y':0.9,
                              'x':0.5,
                              'xanchor': 'center',
                              'yanchor': 'top'}
                          , yaxis_title="Изменение, % год к году",)
        return fig
