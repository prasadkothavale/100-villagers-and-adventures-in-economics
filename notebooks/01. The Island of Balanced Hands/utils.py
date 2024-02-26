from random import randrange
from csv import DictReader

precision = precision if 'precision' in vars() or 'precision' in globals() else 4

def is_almost_zero(number):
    return round(number, precision) == 0

def is_surplus(number):
    return round(number, precision) > 0

def is_deficit(number):
    return round(number, precision) < 0

def pick_random_from(collection):
    return list(collection)[randrange(len(collection))]

def default_round(number):
    return round(number, precision)

def load_csv(file):
    """ loads csv file to dict """
    with open(file, 'r', encoding='utf-8') as f:
        dict_reader = DictReader(f)
        return list(dict_reader)