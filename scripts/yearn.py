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
from bokeh.layouts import layout

from scripts.formatters import * 

yearn_color = '#006ae3'

def get_yearn_apr():
    api = 'https://api.flipsidecrypto.com/api/v2/queries/a2777d58-0b3e-4d24-b883-0263256759ca/data/latest'
    
    response = requests.get(api)
    print('Retrieved data')
    df = pd.DataFrame(response.json())
    df['BLOCK_TIMESTAMP'] = pd.to_datetime(df['BLOCK_TIMESTAMP']).dt.tz_localize(None)
    df['DATE_STR'] = df['BLOCK_TIMESTAMP'].dt.strftime("%d %b, %y")
    return df.sort_values('BLOCK_TIMESTAMP').reset_index(drop=True)

def get_yearn_hodl():
    api = 'https://api.flipsidecrypto.com/api/v2/queries/a85460ae-2403-45c6-a603-9b1f1acf5033/data/latest'

    response = requests.get(api)
    print('Retrieved data')
    df = pd.DataFrame(response.json())
    df['BALANCE_DATE'] = pd.to_datetime(df['BALANCE_DATE']).dt.tz_localize(None)
    df['DATE_STR'] = df['BALANCE_DATE'].dt.strftime("%d %b, %y")

    return df.sort_values('BALANCE_DATE').reset_index(drop=True)


yearn_apr_df = get_yearn_apr()
yearn_stat_df = get_yearn_hodl()

def yearn_apr_plot():

    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')

    p.varea(source=cds(yearn_apr_df),x='BLOCK_TIMESTAMP',y2='APR',y1=0 ,fill_color=yearn_color,fill_alpha=0.7)
    line = p.line(source=cds(yearn_apr_df),x='BLOCK_TIMESTAMP',y='APR',line_color=yearn_color,line_width=2)

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
        <h3> @APR </h3>
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

    apr_script,apr_div = components(p)

    latest = format_number(yearn_apr_df[yearn_apr_df['BLOCK_TIMESTAMP']==yearn_apr_df['BLOCK_TIMESTAMP'].max()]['APR'].reset_index(drop=True)[0])

    out_dict = {
        "script":apr_script,
        "div":apr_div,
        "latest":latest
    }

    return out_dict

def yearn_hodler_plot():

    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')

    bar = p.vbar(source=cds(yearn_stat_df),x='BALANCE_DATE',top='HODLERS',fill_color=yearn_color,fill_alpha=0.7,line_alpha=0,hover_alpha=1,width=timedelta(days=0.7))

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
        <h3> @HODLERS </h3>
        <h7> @DATE_STR </h7>
        </div>
        """
    hover = HoverTool(tooltips = tooltips ,callback=callback, mode='vline',renderers=[bar])

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

    apr_script,apr_div = components(p)

    latest = (yearn_stat_df[yearn_stat_df['BALANCE_DATE']==yearn_stat_df['BALANCE_DATE'].max()]['HODLERS'].reset_index(drop=True)[0])

    out_dict = {
        "script":apr_script,
        "div":apr_div,
        "latest":latest
    }

    return out_dict

def yearn_hodled_plot():

    yearn_stat_df['STETH_HODLED_STR'] = yearn_stat_df['STETH_HODLED'].apply(format_number)

    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')

    line = p.line(source=cds(yearn_stat_df),x='BALANCE_DATE',y='STETH_HODLED',color=yearn_color,line_width=2)
    p.varea(source=cds(yearn_stat_df),x='BALANCE_DATE',y1='STETH_HODLED',y2=0,fill_color=yearn_color,alpha=0.7)

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
        <h3> @STETH_HODLED_STR </h3>
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

    apr_script,apr_div = components(p)

    latest = yearn_stat_df[yearn_stat_df['BALANCE_DATE']==yearn_stat_df['BALANCE_DATE'].max()]['STETH_HODLED_STR'].reset_index(drop=True)[0]

    out_dict = {
        "script":apr_script,
        "div":apr_div,
        "latest":latest
    }

    return out_dict
