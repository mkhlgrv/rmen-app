import json
import os

from dotenv import load_dotenv
load_dotenv()
from dash import Input, Output, Dash, State, dash_table, dcc, html
import pickle
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash.exceptions import PreventUpdate
from rmen.forecast import Forecast
from rmen.variable import Variable
from rmen.model import Model
from rmen.statistic import Statistic
from dash.dash_table import FormatTemplate
percentage = FormatTemplate.percentage(2)


help_text =  dcc.Markdown("""
На этой странице вы можете получить обновляемые в реальном времени прогнозы моделей машинного обучения для основных макроэкономических показателей.
- Выберите переменную и горизонт прогнозирования. 
Например, для квартального ряда ВВП горизонт прогнозирования 0 соответствует прогнозу для текущего периода.
- Выберите доступные модели из списка.
- Получите псевдоисторический вневыборочный прогноз, значения метрик качества моделей и предсказания на актуальную дату.
- Скачайте Excel-файл cо значениями прогноза для выбранных моделей или
 получите подробную информацию о конфигурации моделей в формате JSON.
""")

forecast_path = os.path.join(os.getenv("project_dir"), "assets","model","forecast.pickle")
with open(forecast_path, 'rb') as f:
    forecast_list = pickle.load(f)


variable_options = [{"label":i, "value":i} for i in set([f.variable.name["rus"] for i, f in enumerate(forecast_list)])]
horizon_options = [{"label":str(i), "value":i} for i in set([f.horizon for i, f in enumerate(forecast_list)])]
# dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")
external_stylesheets = [dbc.themes.LUX]
load_figure_template("lux")


app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Прогнозирование макроэкономических переменных"

table = dash_table.DataTable(
        id='model',
        columns=[
            {"name": label, "id": i} for i, label in zip(["id","name", "desc"],["id","Модель", "Описание"])
        ],
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
    style_cell_conditional=[
            {
            'if': {'column_id': c},
            'display': 'none'
            } for c in ['id']
            ]
    )



metric = dash_table.DataTable(
        id='metric',
        columns=[
            {"name": label, "id": i, "type":"numeric", "format":percentage} for label,i
                in zip(["Модель","R2", "RMSE", "MaxErr","MAE"],["model","R2", "RMSE", "MaxErr","MAE"])
        ],
        page_current= 0,
        page_size= 10
    )


controls = html.Div(children = [help_text, html.Div("Выберите переменную")
                     , dcc.Dropdown(id='variable',
                                    options=variable_options,
                                    value = variable_options[0]["value"]
                                    )
                     , html.Div("Выберите горизонт прогнозирования")
                     , dcc.Dropdown(id='horizon',
                                  options=horizon_options,
                                    value  = horizon_options[0]["value"]
                                  )
                    , html.Div("Выберите модель")
                    , table
                    , html.Button("Скачать прогноз в Excel", id="btn_xlsx", n_clicks=0)
                    , dcc.Download(id="download-dataframe-xlsx")
                    , html.Button("Скачать прогноз и метаданные в JSON", id="btn_json", n_clicks=0)
                    , dcc.Download(id="download-json")
                    ]
                    ,style={'float': 'left', 'width': '100%', 'margin-left':'15px'
                        , 'margin-top':'7px', 'margin-right':'7px'})


plot = html.Div(dcc.Graph(id="plot"))

header = html.H3("Прогнозирование макроэкономических переменных")
app.layout = html.Div(children = [
                    dbc.Row(
                          dbc.Col(header))
                    ,dbc.Row(children =[
                          dbc.Col(controls, width = 4)
                        , dbc.Col(children=[dbc.Row(plot)
                                           , dbc.Row(metric)], width = 8
                                 )
                    ]
                            )
                    ]
                    )

@app.callback(
    Output('model', 'data'),
    [Input('variable', 'value'),
    Input('horizon', 'value')])
def update_model_table_data(variable, horizon):
        return [{'id':i, 'name': f.name, 'desc': f.desc} for i, f
              in enumerate(forecast_list) 
                    if f.variable.name["rus"] == variable
                    and f.horizon == horizon
              ]


@app.callback(
    Output("download-dataframe-xlsx", "data"),
    State('model', 'selected_row_ids'),
    Input("btn_xlsx", "n_clicks"),
    prevent_initial_call=True,
)
def download_xlsx(idx,n_clicks):
    if idx is not None and len(idx)>0:
        forecast = [forecast_list[i] for i in idx]
        stat = Statistic(forecast[0].variable, forecast)
        df = stat.to_file("csv")
        return dcc.send_data_frame(df.to_excel, "ml_forecast.xlsx", sheet_name="Лист1")


    
@app.callback(
    Output("download-json", "data"),
    State('model', 'selected_row_ids'),
    Input("btn_json", "n_clicks"),
    prevent_initial_call=True,
)
def download_json(idx,n_clicks):
    if idx is not None and len(idx)>0:
        forecast = [forecast_list[i] for i in idx]
        stat = Statistic(forecast[0].variable, forecast)
        out = stat.to_file("json")
        out = json.dumps(out, ensure_ascii=False)#.encode('utf8')
        return dict(content=out, filename="ml_forecast.json")


@app.callback(
    Output(component_id='metric', component_property='data'),
    Input(component_id='model', component_property='selected_row_ids'),
     PreventUpdate=True
)
def show_table(idx):
    if idx is not None and len(idx)>0:
        forecast = [forecast_list[i] for i in idx]
        stat = Statistic(forecast[0].variable, forecast)
        metrics = stat.show_metric()
        names = ["model","R2", "RMSE", "MaxErr","MAE"]
        return [{label: i for label, i in zip(names, row)} for row in metrics]
    else:
        raise PreventUpdate

@app.callback(
    Output(component_id='plot', component_property='figure'),
    Input(component_id='model', component_property='selected_row_ids'),
    prevent_initial_call = True
)
def show_plot(idx):
    if idx is not None and len(idx)>0:
        forecast = [forecast_list[i] for i in idx]
        return Statistic(forecast[0].variable, forecast, "2020-01-01").plotly(show_ci=True)
    else:
        raise PreventUpdate



if __name__ == '__main__':
    app.run_server(port = 8050, debug=True)


