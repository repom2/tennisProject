import pandas as pd
import itertools
from vakio.models import Combination
import os

"""
    13 kohdetta oikein 26 %
    12 kohdetta oikein 13 %
    11 kohdetta oikein 9 %
    10 kohdetta oikein 15 %.
"""
lst = [
    [1, 1.21, 8.0, 16.5],
    [2, 1.92, 3.95, 4.15],
    [3, 1.23, 7.15, 14.2],
    [4, 1.48, 4.9, 7.15],
    [5, 3.65, 3.5, 2.17],
    [6, 1.68, 4.2, 5.06],
    [7, 1.53, 4.59, 6.5],
    [8, 1.9, 3.55, 4.51],
    [9, 3.04, 3.25, 2.65],
    [10, 3.2, 3.6, 2.25],
    [11, 3.2, 3.72, 2.25],
    [12, 1.833, 3.61, 4.81],
    [13, 2.4, 3.26, 3.29],
]


def arbitrage_check(i):
    if(1 / i[1] + 1 / i[2] + 1 / i[3]) < 1:
        print("Arbitage found!")


def join_set(s):
    return ''.join(s)


# Function to calculate probability
def calculate_prob(combination, df):
    p = 1
    for i, outcome in enumerate(combination):
        p *= df.loc[i, outcome]
    return round(p, 8)


def calculate_probabilities():
    for i in lst:
        arbitrage_check(i)
    cost = 0.1
    winshare = 330000 * 0.26 + 100000 # 13 kohdetta oikein 26 %
    winshare = 60000 * 0.26
    df = pd.DataFrame(lst, columns=['line', 'home', 'draw', 'away'])
    df['1%'] = 1 / df['home']
    df['X%'] = 1 / df['draw']
    df['2%'] = 1 / df['away']
    df['%'] = 1 - (df['X%'] + df['2%'] + df['1%'] - 1)
    df['1'] = df['%'] * df['1%']
    df['2'] = df['%'] * df['2%']
    df['X'] = df['%'] * df['X%']

    outcomes = ['1', 'X', '2']

    print(df[['line', '1', 'X', '2']])

    # Generate all possible combinations for 12 matches
    combinations = list(itertools.product(outcomes, repeat=len(df)))

    print('Number of combinations: ', len(combinations))

    probabilities = [calculate_prob(combo, df) for combo in combinations]

    df = pd.DataFrame({
        "prob": probabilities,
        "combination": combinations,
    })

    df['id'] = df['combination'].apply(join_set)

    Combination.objects.all().delete()
    df = df[['id', 'prob']]
    data_dict = df.to_dict('records')
    instances = [Combination(**data) for data in data_dict]

    Combination.objects.bulk_create(instances)
