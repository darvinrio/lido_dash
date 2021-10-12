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

def get_lido_price():
    api = 'https://api.flipsidecrypto.com/api/v2/queries/42891802-d5e9-42b6-afe1-2b961eb352b2/data/latest'
    
    response = requests.get(api)
    print('Retrieved data')
    df = pd.DataFrame(response.json())
    df['HOUR'] = pd.to_datetime(df['HOUR']).dt.tz_localize(None)
    df['DATE_STR'] = df['HOUR'].dt.strftime("%d %b, %y")
    return df.sort_values('HOUR').reset_index(drop=True)

price_df = get_lido_price()


def price_plot():
    price_df['STETH_PRICE_STR'] = price_df['STETH_PRICE'].apply(format_money) 
    price_df['ETH_PRICE_STR'] = price_df['ETH_PRICE'].apply(format_money) 

    p_line = figure(x_axis_type='datetime',plot_height=400,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')
    line = p_line.line(source=cds(price_df),x='HOUR',y='STETH_PRICE',line_color='green',line_width=2,legend_label='stETH')
    p_line.line(source=cds(price_df),x='HOUR',y='ETH_PRICE',line_color='blue',alpha=0.5,line_width=2,legend_label='ETH')
    p_line.legend.click_policy="hide"

    crosshair = CrosshairTool(dimensions='height',line_alpha=0.5)

    callback = CustomJS(args={'p': p_line}, code="""
        var tooltips = document.getElementsByClassName("bk-tooltip");
        const tw = 100;
        for (var i = 0; i < tooltips.length; i++) {
            tooltips[i].style.top = '10px'; 
            tooltips[i].style.left = p.width/6 + 'px'; 
            tooltips[i].style.width = tw + 'px'; 
        } """)

    tooltips = """
        <div>
        <h7> @DATE_STR </h7>
        <h6> stETH -  @STETH_PRICE_STR </h6>
        <h6> ETH - @ETH_PRICE_STR </h6>
        </div>
        """
    hover = HoverTool(tooltips = tooltips ,callback=callback, mode='vline',renderers=[line])

    hover.show_arrow = False
    p_line.outline_line_color = None
    p_line.add_tools(hover,crosshair)

    p_line.xaxis.formatter = DatetimeTickFormatter(days="%b %d",months="%b %y")
    p_line.yaxis.formatter=NumeralTickFormatter(format="$0.00 a")

    p_line.yaxis.minor_tick_line_color = None
    p_line.yaxis.major_tick_line_color = None
    p_line.xaxis.minor_tick_line_color = None
    p_line.xaxis.major_tick_line_color = None
    p_line.xaxis.axis_line_color = None
    p_line.yaxis.axis_line_color = None
    p_line.xaxis.visible = False
    # p_line.grid.visible=False

    p_bar = figure(x_axis_type='datetime',plot_height=200,sizing_mode="stretch_width",tools='xwheel_zoom,ywheel_zoom,xpan,reset')
    bar = p_bar.vbar(source=cds(price_df),x='HOUR',top='STETH_DIFF',color='COLOR',fill_alpha=0.7,line_alpha=0,hover_alpha=1,width=timedelta(days=0.7))


    crosshair = CrosshairTool(dimensions='height',line_alpha=0.5)

    callback = CustomJS(args={'p': p_bar}, code="""
        var tooltips = document.getElementsByClassName("bk-tooltip");
        const tw = 100;
        for (var i = 0; i < tooltips.length; i++) {
            tooltips[i].style.top = '10px'; 
            tooltips[i].style.left = p.width/6 + 'px'; 
            tooltips[i].style.width = tw + 'px'; 
        } """)

    tooltips = """
        <div>
        <h7> @DATE_STR </h7>
        <h6> @STETH_DIFF $ </h6>
        </div>
        """
    hover = HoverTool(tooltips = tooltips ,callback=callback, mode='vline',renderers=[bar])

    hover.show_arrow = False
    p_bar.outline_line_color = None
    p_bar.add_tools(hover,crosshair)

    p_bar.xaxis.formatter = DatetimeTickFormatter(days="%b %d",months="%b %y")
    p_bar.yaxis.formatter=NumeralTickFormatter(format="$ 0.00 a")

    p_bar.yaxis.minor_tick_line_color = None
    p_bar.yaxis.major_tick_line_color = None
    p_bar.xaxis.minor_tick_line_color = None
    p_bar.xaxis.major_tick_line_color = None
    p_bar.xaxis.axis_line_color = None
    p_bar.yaxis.axis_line_color = None
    # p_bar.grid.visible=False


    plot = layout([p_line,p_bar],sizing_mode="stretch_width")

    price_script,price_div = components(plot)

    latest_steth = latest = format_money(price_df[price_df['HOUR']==price_df['HOUR'].max()]['STETH_PRICE'].reset_index(drop=True)[0])
    latest_eth = latest = format_money(price_df[price_df['HOUR']==price_df['HOUR'].max()]['ETH_PRICE'].reset_index(drop=True)[0])

    out_dict = {
        "script":price_script,
        "div":price_div,
        "latest_steth":latest_steth,
        "latest_eth":latest_eth,
    }

    return out_dict