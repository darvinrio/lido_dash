from flask import Flask, render_template, url_for, request, redirect

import socket
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [response
            for response in responses
            if response[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

from scripts.bal import lido_bal_plot
from scripts.price import price_plot
from scripts.anchor import anc_plot,anc_farm_plot,anc_hodled_plot,anc_hodler_plot
from scripts.lido_apr import apr_plot,beth_balance,lido_hodler_plot,lido_hodled_plot
from scripts.yearn import yearn_apr_plot,yearn_hodler_plot,yearn_hodled_plot
from scripts.crv_pool import pool_bal_plot, pool_current_plot

app = Flask(__name__)

lido_bal_dict =  lido_bal_plot()
price_dict = price_plot()
beth_bal_dict = beth_balance()
crv_pool_dict = pool_bal_plot()
crv_current_dict = pool_current_plot()

anc_dict = anc_plot()
anc_farm_dict = anc_farm_plot()
anc_holders = anc_hodler_plot()
anc_hodled = anc_hodled_plot()

apr_dict = apr_plot()
lido_holders = lido_hodler_plot()
lido_hodled = lido_hodled_plot()

yearn_apr_dict = yearn_apr_plot()
yearn_holders = yearn_hodler_plot()
yearn_hodled = yearn_hodled_plot()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dash')
def dash():

    return render_template(
        'dash.html',
        lido_bal_dict=lido_bal_dict,
        price_dict=price_dict,
        beth_bal_dict=beth_bal_dict,
        crv_pool_dict=crv_pool_dict,
        crv_current_dict=crv_current_dict,

        hodl_apr=apr_dict['latest'],
        hodlers=lido_holders['latest'],
        hodled=lido_hodled['latest'],

        yearn_apr = yearn_apr_dict['latest'],
        yearn_hodlers=yearn_holders['latest'],
        yearn_hodled=yearn_hodled['latest'],

        anc_borrow_apr = anc_farm_dict['latest_borrow'],
        anc_deposit_apr = anc_farm_dict['latest_dep'],
        anc_hodlers=anc_holders['latest'],
        anc_hodled=anc_hodled['latest'],
    )



@app.route('/hodl')
def hodl():
    return render_template(
        'hodl.html',
        apr_dict=apr_dict,
        lido_holders=lido_holders,
        lido_hodled=lido_hodled
    )

@app.route('/anc')
def anchor():
    return render_template(
        'anchor.html',
        anc_dict=anc_dict,
        anc_farm_dict=anc_farm_dict,
        anc_holders=anc_holders,
        anc_hodled=anc_hodled
    )

@app.route('/yearn')
def yearn():
    return render_template(
        'yearn.html',
        yearn_apr_dict=yearn_apr_dict,
        yearn_holders=yearn_holders,
        yearn_hodled=yearn_hodled
    )

@app.route('/docs')
def docs():
    return render_template('docs.html')

if __name__ == "__main__":
    app.run(debug=True)