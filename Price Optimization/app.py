from os import link
from pydoc import classname
import dash
import pandas as pd
import numpy as np
from dash import dash_table
import logging
import plotly.graph_objs as go
import plotly.express as px
# import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import Python.optimize_price
import Python.optimize_quantity
import dash_daq as daq

group_colors = {"control": "light blue", "reference": "red"}

app = dash.Dash(
    __name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width"}], title="Price Optimization", update_title="Updating... Pls wait !"
    # link=[
    #     {"rel":"icon","href":"https://149510500.v2.pressablecdn.com/wp-content/uploads/2021/07/cropped-FAV-ICON-cropped-UBTI_Globe-32x32.png","sizes":"32x32"}
    # ]
)
# app._favicon = ("asses")

server = app.server

# Load the data
df = pd.read_csv('Data/price.csv')
df.head(10)

# App Layout
app.layout = html.Div(
    children=[
        # Error Message
        html.Div(id="error-message"),
        # Top Banner
        html.Div(
            className="study-browser-banner row",
            children=[
                html.Img(
                    className="logo", src=app.get_asset_url("tag2.svg")
                ),
                html.H2(className="h2-title",
                        children="Price Optimization using Machine Learning  "),
                html.Img(
                    className="logo", src=app.get_asset_url("tag2.svg")
                ),


            ],
            style={
                'textAlign': 'center'
            }
        ),

        html.Div(

            # className="padding-top-bot",
            children=[
                html.Div(
                    [
                        html.H6("Optimize"),
                        dcc.RadioItems(
                            id="selected-var-opt",
                            className="radioBtns",

                            inline=True,
                            options=[
                                {
                                    "label": "Price",
                                    "value": "price"
                                },
                                {
                                    "label": "Quantity",
                                    "value": "quantity"
                                },

                            ],
                            value="price",
                            # labelStyle={
                            #     "display": "inline-block",
                            #     "padding": "12px 12px 12px 12px",
                            # },
                        ),

                    ],
                    className='filter'
                ),
                html.Div(
                    [
                        html.H6("Optimization Range"),
                        html.Div(id='output-container-range-slider',
                                 className="rangeSlider"),
                        dcc.RangeSlider(
                            id='my-range-slider', min=0, max=500, step=1,
                            marks={
                                0: '0',
                                500: '500'
                            },
                            value=[200, 400]
                        )
                    ],
                    className='filter'

                ),
                html.Div(
                    [
                        html.H6("Fixed Cost"),
                        daq.NumericInput(
                            id="selected-cost-opt",
                            min=0,
                            max=10000,
                            value=80
                        ),
                    ],
                    className='filter'
                )

            ],
            className="baseDiv row",
            id="cross-filter-options",
        ),
        html.Div(
            children=[
                html.H6("Recommendation : "),
                html.Div(id='id-insights', style={'color': 'DarkCyan', 'fontSize': 15}
                         )
            ],
            className="recommend"
        ),

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            className="card halfwidth",
                            children=[
                                # html.Div(id="table1"),
                                html.H6("PRICE OPTIMIZATION RESULT"),
                                dash_table.DataTable(

                                    id='heatmap',
                                    columns=[
                                        {'name': 'Price', 'id': 'Price',
                                         'type': 'numeric'},
                                        {'name': 'Profit', 'id': 'Revenue',
                                         'type': 'numeric'},
                                        {'name': 'Quantity', 'id': 'Quantity',
                                         'type': 'numeric'},
                                    ],
                                    style_data_conditional=[
                                        {
                                            'if': {'row_index': 'odd'},
                                            'backgroundColor': 'rgb(248, 248, 248)'
                                        },
                                        {
                                            'if': {
                                                'row_index': 0,  # number | 'odd' | 'even'
                                                'column_id': 'Revenue'
                                            },
                                            'backgroundColor': 'dodgerblue',
                                            'color': 'white'
                                        },
                                        {
                                            'if': {
                                                'row_index': 0,  # number | 'odd' | 'even'
                                                'column_id': 'Price'
                                            },
                                            'backgroundColor': 'dodgerblue',
                                            'color': 'white'
                                        },
                                        {
                                            'if': {
                                                'row_index': 0,  # number | 'odd' | 'even'
                                                'column_id': 'Quantity'
                                            },
                                            'backgroundColor': 'dodgerblue',
                                            'color': 'white'
                                        },
                                    ],
                                    style_header={
                                        'backgroundColor': 'rgb(230, 230, 230)',
                                        'fontWeight': 'bold',
                                        # 'border': '1px solid black'
                                    },
                                    style_data={
                                        'whiteSpace': 'normal',
                                        'height': 'auto',
                                    },
                                    editable=True,
                                    filter_action="native",
                                    sort_action="native",
                                    page_size=10,

                                )
                            ],
                        ),
                        html.Div(
                            className="card",
                            children=[
                                html.H6("MAXIMIZING PROFIT"),
                                dcc.Graph(id="lineChart1", figure={
                                    'layout': go.Layout(margin={'t': 0, 'b': 0, 'l': 0, 'r': 0, 'pad': 0})}),
                            ],
                        ),
                        html.Div(
                            className="card",
                            children=[
                                html.H6("PRICE VS QUANTITY"),
                                dcc.Graph(id="lineChart2", figure={'layout': go.Layout(
                                    margin={'t': 2, 'b': 2, 'r': 2, 'l': 2})}),
                            ],
                        ),
                    ],
                    className='graphContainer'
                ),

            ]

        )
    ]
)


@ app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('my-range-slider', 'value')])
def update_output(value):
    return "{}".format(value)


@ app.callback(
    [
        Output("heatmap", 'data'),
        Output("lineChart1", 'figure'),
        Output("lineChart2", 'figure'),
        Output("id-insights", 'children'),
    ],
    [
        Input("selected-var-opt", "value"),
        Input("my-range-slider", "value"),
        Input("selected-cost-opt", "value")
    ]
)
def update_output_All(var_opt, var_range, var_cost):

    try:
        if var_opt == 'price':

            res, fig_PriceVsRevenue, fig_PriceVsQuantity, opt_Price, opt_Revenue = Python.optimize_price.fun_optimize(
                var_opt, var_range, var_cost, df)
            res = np.round(res.sort_values(
                'Revenue', ascending=False), decimals=2)

            if opt_Revenue > 0:
                return [res.to_dict('records'), fig_PriceVsRevenue, fig_PriceVsQuantity,
                        f'The maximum profit of {opt_Revenue} is achieved by optimizing {var_opt} of {opt_Price}, fixed cost of {var_cost} and optimization was carried for {var_opt} range between {var_range}']
            else:
                return [res.to_dict('records'), fig_PriceVsRevenue, fig_PriceVsQuantity,
                        f'For the fixed cost of {var_cost} and {var_opt} range between {var_range}, you will incur loss in revenue']

        else:

            res, fig_QuantityVsRevenue, fig_PriceVsQuantity, opt_Quantity, opt_Revenue = Python.optimize_quantity.fun_optimize(
                var_opt, var_range, var_cost, df)
            res = np.round(res.sort_values(
                'Revenue', ascending=False), decimals=2)

            if opt_Revenue > 0:
                return [res.to_dict('records'), fig_QuantityVsRevenue, fig_PriceVsQuantity,
                        f'The maximum profit of {opt_Revenue} is achieved by optimizing {var_opt} of {opt_Quantity}, fixed cost of {var_cost} and optimization was carried for {var_opt} range between {var_range}']
            else:
                return [res.to_dict('records'), fig_QuantityVsRevenue, fig_PriceVsQuantity,
                        f'For the fixed cost of {var_cost} and {var_opt} range between {var_range}, you will incur loss in revenue']
        
    except Exception as e:
        logging.exception('Something went wrong with interaction logic:', e)


if __name__ == "__main__":

    app.run_server(debug=True, use_reloader=True,
                   dev_tools_ui=True, host="0.0.0.0", port="5000")
