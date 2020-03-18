from timeit import timeit

a = """
from prices_eur import prices_eur"""

b = """
with open('prices_eur.json') as j:
    prices_eur = json.load(j)
"""

print(timeit(b, setup="import json", number=10))

print(timeit(a, number=10))

