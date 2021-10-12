import pandas as pd
import numpy as np
import requests
import time
import copy
from datetime import datetime as dt
from datetime import timedelta
import json

from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource as cds
from bokeh.models import HoverTool, CrosshairTool, Range1d
from bokeh.models import NumeralTickFormatter, CustomJS,DatetimeTickFormatter
from bokeh.embed import components

from scripts.formatters import * 

lido_color = '#34cdfa'
eth_color = '#454a75'


def get_pool_bal():
    api = 'https://api.flipsidecrypto.com/api/v2/queries/2531fbd8-2cec-4671-a0f6-2c4f6c2796d9/data/latest'
    
    response = requests.get(api)
    print('Retrieved data')
    df = pd.DataFrame(response.json())
    df['BALANCE_DATE'] = pd.to_datetime(df['BALANCE_DATE']).dt.tz_localize(None)
    df['DATE_STR'] = df['BALANCE_DATE'].dt.strftime("%d %b, %y")
    return df.sort_values('BALANCE_DATE').reset_index(drop=True)

pool_df = get_pool_bal() 

def pool_bal_plot():

    pool_df['TOTAL_STETH_STR'] = pool_df['TOTAL_STETH'].apply(format_number) 
    pool_df['TOTAL_ETH_STR'] = pool_df['TOTAL_ETH'].apply(format_number) 

    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')
    line = p.line(source=cds(pool_df),x='BALANCE_DATE',y='LP_TOKENS',line_color=lido_color,line_width=2)
    p.vbar(source=cds(pool_df),x='BALANCE_DATE',top='LP_TOKENS',bottom='TOTAL_STETH',color=eth_color,fill_alpha=0.7,line_alpha=0,hover_alpha=1,width=timedelta(days=0.7))
    p.vbar(source=cds(pool_df),x='BALANCE_DATE',top='TOTAL_STETH',color=lido_color,fill_alpha=0.7,line_alpha=0,hover_alpha=1,width=timedelta(days=0.7))

    crosshair = CrosshairTool(dimensions='height',line_alpha=0.5)

    callback = CustomJS(args={'p': p}, code="""
        var tooltips = document.getElementsByClassName("bk-tooltip");
        const tw = 100;
        for (var i = 0; i < tooltips.length; i++) {
            tooltips[i].style.top = '10px'; 
            tooltips[i].style.left = p.width/6 + 'px'; 
            tooltips[i].style.width = tw + 'px'; 
        } """)

    tooltips = """
        <div>
        <h7> @DATE_STR </h7> <br>
        stETH
        <h4> @TOTAL_STETH_STR </h4> 
        ETH
        <h4> @TOTAL_ETH_STR </h4>
        </div>
        """
    hover = HoverTool(tooltips = tooltips ,callback=callback, mode='vline',renderers=[line])

    hover.show_arrow = False
    # p.outline_line_color = None
    p.add_tools(hover,crosshair)

    p.xaxis.formatter = DatetimeTickFormatter(days="%b %d",months="%b %y")
    p.yaxis.formatter=NumeralTickFormatter(format="0.00 a")


    p.yaxis.minor_tick_line_color = None
    p.yaxis.major_tick_line_color = None
    p.xaxis.minor_tick_line_color = None
    p.xaxis.major_tick_line_color = None
    p.xaxis.axis_line_color = None
    p.yaxis.axis_line_color = None
    p.grid.visible=False

    lido_script,lido_div = components(p)

    latest_steth = format_number(pool_df[pool_df['BALANCE_DATE']==pool_df['BALANCE_DATE'].max()]['TOTAL_STETH'].reset_index(drop=True)[0])
    latest_eth = format_number(pool_df[pool_df['BALANCE_DATE']==pool_df['BALANCE_DATE'].max()]['TOTAL_ETH'].reset_index(drop=True)[0])

    out_dict = {
        "script":lido_script,
        "div":lido_div,
        "latest_steth":latest_steth,
        "latest_eth":latest_eth
    }

    return out_dict



    