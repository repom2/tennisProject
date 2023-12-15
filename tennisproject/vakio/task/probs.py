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
    [1, 1.31, 5.6, 12.0],
    [2, 2.12, 3.76, 3.55],
    [3, 1.74, 4.23, 4.63],
    [4, 1.94, 3.88, 4.0],
    [5, 1.9, 3.75, 4.3],
    [6, 1.84, 4.2, 4.38],
    [7, 4.3, 4.33, 1.78],
    [8, 3.4, 2.9, 2.6],
    [9, 2.58, 3.6, 2.9],
    [10, 2.87, 3.4, 2.63],
    [11, 1.74, 4.42, 4.44],
    [12, 3.07, 3.6, 2.45],
]


def join_set(s):
    return ''.join(s)


# Function to calculate probability
def calculate_prob(combination, df):
    p = 1
    for i, outcome in enumerate(combination):
        p *= df.loc[i, outcome]
    return round(p, 8)


def calculate_probabilities():
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

    # (odds - 1) * stake = winshare
    # odds = winshare / stake + 1
    odds = winshare / cost + 1
    probabilty = 1 / odds
    df = df[df['prob'] >= probabilty]

    print('Number of combinations with probability ', probabilty, len(df))

    df['id'] = df['combination'].apply(join_set)

    Combination.objects.all().delete()
    df = df[['id', 'prob']]
    data_dict = df.to_dict('records')
    instances = [Combination(**data) for data in data_dict]

    Combination.objects.bulk_create(instances)
