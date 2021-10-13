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

anc_color ='#4bdb4b'

def get_anc_stats():
    api = 'https://api.flipsidecrypto.com/api/v2/queries/d7cc7df4-d264-439e-b9c3-5eb84069bcac/data/latest'
    
    response = requests.get(api)
    print('Retrieved data')
    df = pd.DataFrame(response.json())
    df['DATE'] = pd.to_datetime(df['DATE']).dt.tz_localize(None)
    df['DATE_STR'] = df['DATE'].dt.strftime("%d %b, %y")
    return df.sort_values('DATE').reset_index(drop=True)

def get_anc_hodl():
    api = 'https://api.flipsidecrypto.com/api/v2/queries/b89088ba-4f58-400f-a768-d2ba76102bf8/data/latest'

    response = requests.get(api)
    print('Retrieved data')
    df = pd.DataFrame(response.json())
    df['DATE'] = pd.to_datetime(df['DATE']).dt.tz_localize(None)
    df['DATE_STR'] = df['DATE'].dt.strftime("%d %b, %y")

    return df.sort_values('DATE').reset_index(drop=True)

anc_df = get_anc_stats()
anc_df['ANC_DIST_APR'] = anc_df['ANC_DIST_APR']+10
anc_df['ANC_FARM_APR'] = anc_df['ANC_DIST_APR']-anc_df['DAILY_MEAN_BORROW_APR']

anc_stat_df = get_anc_hodl()


def anc_plot():
  
    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')

    line = p.line(source=cds(anc_df),x='DATE',y='ANC_DIST_APR',line_color='green',line_width=2,legend_label='dist. APR')
    line = p.line(source=cds(anc_df),x='DATE',y='DAILY_MEAN_BORROW_APR',line_color='red',line_width=2,legend_label='borrow APR')
    line = p.line(source=cds(anc_df),x='DATE',y='ANC_FARM_APR',line_color='blue',line_width=2,legend_label='net APR')
    p.legend.click_policy="hide"

    crosshair = CrosshairTool(dimensions='height',line_alpha=0.5)

    callback = CustomJS(args={'p': p}, code="""
        var tooltips = document.getElementsByClassName("bk-tooltip");
        const tw = 100;
        for (var i = 0; i < tooltips.length; i++) {
            tooltips[i].style.top = '10px'; 
            tooltips[i].style.left = p.width/4 + 'px'; 
            tooltips[i].style.width = tw + 'px'; 
        } """)

    tooltips = """
        <div>
        <h7> @DATE_STR </h7>
        <h6> Dist APR -  @ANC_DIST_APR </h6>
        <h6> Borrow APR - @DAILY_MEAN_BORROW_APR </h6>
        <h6> net gain APR - @ANC_FARM_APR </h6>
        </div>
        """
    hover = HoverTool(tooltips = tooltips ,callback=callback, mode='vline',renderers=[line])

    hover.show_arrow = False
    p.outline_line_color = None
    p.add_tools(hover,crosshair)

    p.xaxis.formatter = DatetimeTickFormatter(days="%b %d",months="%b %y")
    p.yaxis.formatter=NumeralTickFormatter(format="0.00 ")

    p.yaxis.minor_tick_line_color = None
    p.yaxis.major_tick_line_color = None
    p.xaxis.minor_tick_line_color = None
    p.xaxis.major_tick_line_color = None
    p.xaxis.axis_line_color = None
    p.yaxis.axis_line_color = None
    # p.xaxis.visible = False
    # p.grid.visible=False

    anc_script,anc_div = components(p)

    out_dict = {
        "anc_script":anc_script,
        "anc_div":anc_div,
    }

    return out_dict

def anc_farm_plot():

    ltv1 = 0.3
    ltv2 = 0.45
    anc_df['bETH_FARM1'] = ltv1*anc_df['ANC_FARM_APR']
    anc_df['dep_bETH_FARM1'] = (0.2+ltv1)*anc_df['ANC_FARM_APR']
    anc_df['bETH_FARM2'] = ltv2*anc_df['ANC_FARM_APR']
    anc_df['dep_bETH_FARM2'] = (0.2+ltv2)*anc_df['ANC_FARM_APR']

    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')
    p.varea(source=cds(anc_df),x='DATE',y2='bETH_FARM1',y1='bETH_FARM2' ,fill_color='blue',fill_alpha=0.5,legend_label='Borrow farming')
    p.varea(source=cds(anc_df),x='DATE',y2='dep_bETH_FARM1',y1='dep_bETH_FARM2' ,fill_color='red',fill_alpha=0.5,legend_label='Borrow+Deposit farming')
    line = p.line(source=cds(anc_df),x='DATE',y='dep_bETH_FARM1',line_color=None,line_width=2)
    
    p.legend.click_policy="hide"

    crosshair = CrosshairTool(dimensions='height',line_alpha=0.5)

    callback = CustomJS(args={'p': p}, code="""
        var tooltips = document.getElementsByClassName("bk-tooltip");
        const tw = 100;
        for (var i = 0; i < tooltips.length; i++) {
            tooltips[i].style.top = '10px'; 
            tooltips[i].style.left = p.width/2 + 'px'; 
            tooltips[i].style.width = tw + 'px'; 
        } """)

    tooltips = """
        <div>
        borrow farming 
        <h6> @bETH_FARM1 to  @bETH_FARM2 APR</h6>
        borrow+deposit farming
        <h6> @dep_bETH_FARM1 to  @dep_bETH_FARM2 APR</h6>
        <h7> @DATE_STR </h7>
        </div>
        """
    hover = HoverTool(tooltips = tooltips ,callback=callback, mode='vline',renderers=[line])

    hover.show_arrow = False
    p.outline_line_color = None
    p.add_tools(hover,crosshair)

    p.xaxis.formatter = DatetimeTickFormatter(days="%b %d",months="%b %y")
    p.yaxis.formatter=NumeralTickFormatter(format="0.00 ")

    p.yaxis.minor_tick_line_color = None
    p.yaxis.major_tick_line_color = None
    p.xaxis.minor_tick_line_color = None
    p.xaxis.major_tick_line_color = None
    p.xaxis.axis_line_color = None
    p.yaxis.axis_line_color = None
    # p.xaxis.visible = False
    # p.grid.visible=False

    farm_script,farm_div = components(p)

    latest_dep = format_number(anc_df[anc_df['DATE']==anc_df['DATE'].max()]['dep_bETH_FARM2'].reset_index(drop=True)[0])
    latest_borrow = format_number(anc_df[anc_df['DATE']==anc_df['DATE'].max()]['bETH_FARM2'].reset_index(drop=True)[0])


    out_dict = {
        "farm_script":farm_script,
        "farm_div":farm_div,
        "latest_borrow":latest_borrow,
        "latest_dep":latest_dep
    }

    return out_dict


def anc_hodler_plot():

    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')

    bar = p.vbar(source=cds(anc_stat_df),x='DATE',top='USERS',fill_color=anc_color,fill_alpha=0.7,line_alpha=0,hover_alpha=1,width=timedelta(days=0.7))

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
        <h3> @USERS </h3>
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

    latest = (anc_stat_df[anc_stat_df['DATE']==anc_stat_df['DATE'].max()]['USERS'].reset_index(drop=True)[0])

    out_dict = {
        "script":apr_script,
        "div":apr_div,
        "latest":latest
    }

    return out_dict

def anc_hodled_plot():

    anc_stat_df['BETH_DEP_STR'] = anc_stat_df['BETH_DEP'].apply(format_number)

    p = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')

    line = p.line(source=cds(anc_stat_df),x='DATE',y='BETH_DEP',color=anc_color,line_width=2)
    p.varea(source=cds(anc_stat_df),x='DATE',y1='BETH_DEP',y2=0,fill_color=anc_color,alpha=0.7)

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
        <h3> @BETH_DEP_STR </h3>
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

    latest = anc_stat_df[anc_stat_df['DATE']==anc_stat_df['DATE'].max()]['BETH_DEP_STR'].reset_index(drop=True)[0]

    out_dict = {
        "script":apr_script,
        "div":apr_div,
        "latest":latest
    }

    return out_dict
