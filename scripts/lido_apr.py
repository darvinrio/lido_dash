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

lido_color = '#34cdfa'
anc_color ='#4bdb4b'

def get_lido_apr_beth_bal():
    api = 'https://api.flipsidecrypto.com/api/v2/queries/a92bf143-8880-4d98-b65c-afe97c881678/data/latest'

    response = requests.get(api)
    print('Retrieved data')
    df = pd.DataFrame(response.json())
    df['DATE'] = pd.to_datetime(df['DATE']).dt.tz_localize(None)
    df['DATE_STR'] = df['DATE'].dt.strftime("%d %b, %y")
    df = df[df['APR']<20].reset_index(drop=True)

    return df.sort_values('DATE').reset_index(drop=True)

def get_lido_hodl():
    api = 'https://api.flipsidecrypto.com/api/v2/queries/67f5b3b9-1bf6-4014-bb6d-70682666d1a9/data/latest'

    response = requests.get(api)
    print('Retrieved data')
    df = pd.DataFrame(response.json())
    df['BALANCE_DATE'] = pd.to_datetime(df['BALANCE_DATE']).dt.tz_localize(None)
    df['DATE_STR'] = df['BALANCE_DATE'].dt.strftime("%d %b, %y")

    return df.sort_values('BALANCE_DATE').reset_index(drop=True)

df = get_lido_apr_beth_bal()
lido_stat_df = get_lido_hodl()

def apr_plot():

    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')

    p.varea(source=cds(df),x='DATE',y2='APR',y1=0 ,fill_color=lido_color,fill_alpha=0.7)
    line = p.line(source=cds(df),x='DATE',y='APR',line_color=lido_color,line_width=2)

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

    latest = format_number(df[df['DATE']==df['DATE'].max()]['APR'].reset_index(drop=True)[0])

    out_dict = {
        "script":apr_script,
        "div":apr_div,
        "latest":latest
    }

    return out_dict


def lido_hodler_plot():

    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')

    bar = p.vbar(source=cds(lido_stat_df),x='BALANCE_DATE',top='HODLERS',fill_color=lido_color,fill_alpha=0.7,line_alpha=0,hover_alpha=1,width=timedelta(days=0.7))

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

    latest = (lido_stat_df[lido_stat_df['BALANCE_DATE']==lido_stat_df['BALANCE_DATE'].max()]['HODLERS'].reset_index(drop=True)[0])

    out_dict = {
        "script":apr_script,
        "div":apr_div,
        "latest":latest
    }

    return out_dict

def lido_hodled_plot():

    lido_stat_df['STETH_HODLED_STR'] = lido_stat_df['STETH_HODLED'].apply(format_number)

    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')

    line = p.line(source=cds(lido_stat_df),x='BALANCE_DATE',y='STETH_HODLED',color=lido_color,line_width=2)
    p.varea(source=cds(lido_stat_df),x='BALANCE_DATE',y1='STETH_HODLED',y2=0,fill_color=lido_color,alpha=0.7)

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

    latest = lido_stat_df[lido_stat_df['BALANCE_DATE']==lido_stat_df['BALANCE_DATE'].max()]['STETH_HODLED_STR'].reset_index(drop=True)[0]

    out_dict = {
        "script":apr_script,
        "div":apr_div,
        "latest":latest
    }

    return out_dict


def beth_balance():

    df['STETH_BAL_STR'] = df['STETH_BAL'].apply(format_number)

    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')

    p.varea(source=cds(df),x='DATE',y2='STETH_BAL',y1=0 ,fill_color=anc_color,fill_alpha=0.7,hover_alpha=1)
    line = p.line(source=cds(df),x='DATE',y='STETH_BAL',line_color=anc_color,line_width=2)

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
        <h3> @STETH_BAL_STR </h3>
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

    latest = format_number(df[df['DATE']==df['DATE'].max()]['STETH_BAL'].reset_index(drop=True)[0])

    out_dict = {
        "script":apr_script,
        "div":apr_div,
        "latest":latest
    }

    return out_dict
