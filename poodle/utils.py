# utils.py
""" Utility Functions """
import toml


# Read TOML file and return dict
def read_config(fn):
    with open(fn) as fh:
        toml_data = toml.load(fh)
    return toml_data

# Iterate over each stock object in a universe object
def iterate_basket(func):
    def inner(obj, *args, **kwargs):
        for k in obj.stocks.keys():
            func(obj, obj.stocks[k], *args, **kwargs)
    return inner
