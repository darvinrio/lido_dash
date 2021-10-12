import pandas as pd
import numpy as np
import requests
import time
import copy
from datetime import datetime as dt
import json

from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource as cds
from bokeh.models import HoverTool, CrosshairTool, Range1d
from bokeh.models import NumeralTickFormatter, CustomJS,DatetimeTickFormatter
from bokeh.embed import components

from scripts.formatters import * 

lido_color = '#34cdfa'

def get_lido_bal():
    api = 'https://api.flipsidecrypto.com/api/v2/queries/4557ef50-5fe0-443f-8cab-ea07ee7efdc9/data/latest'
    
    response = requests.get(api)
    print('Retrieved data')
    df = pd.DataFrame(response.json())
    df['BALANCE_DATE'] = pd.to_datetime(df['BALANCE_DATE']).dt.tz_localize(None)
    df['DATE_STR'] = df['BALANCE_DATE'].dt.strftime("%d %b, %y")
    return df.sort_values('BALANCE_DATE').reset_index(drop=True)

lido_bal_df = get_lido_bal()

def lido_bal_plot():
    lido_bal_df['BAL_STR'] = lido_bal_df['TOTAL_STETH'].apply(format_number)

    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')
    line = p.line(source=cds(lido_bal_df),x='BALANCE_DATE',y='TOTAL_STETH',line_color=lido_color,line_width=2)
    p.varea(source=cds(lido_bal_df),x='BALANCE_DATE',y2='TOTAL_STETH',y1=0 ,fill_color=lido_color,fill_alpha=0.7)

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
        <h3> @BAL_STR </h3>
        <h7> @DATE_STR </h7>
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

    latest = format_number(lido_bal_df[lido_bal_df['BALANCE_DATE']==lido_bal_df['BALANCE_DATE'].max()]['TOTAL_STETH'].reset_index(drop=True)[0])

    out_dict = {
        "script":lido_script,
        "div":lido_div,
        "latest":latest
    }

    return out_dict

