from numerize import numerize

def no_format(x):
    return '{:.4f}'.format(x)
    


def format_money(x):
    return  "$"+str(numerize.numerize(x))

def format_number(x):
    return  numerize.numerize(x)

def format_fee_percent(x):
    return str(x)+"%"

def format_apr_percent(x):
    return str(round(x*100,3))+"%"