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

list_index = 2
vakio_id = 55520
lst = [
    [1, 0.368, 0.236, 0.396],
    [2, 0.514, 0.222, 0.264],
    [3, 0.481, 0.225, 0.294],

    [4, 0.572, 0.209, 0.219],
    [5, 0.66, 0.22, 0.12],
    [6, 0.47, 0.28, 0.25],

    [7, 0.52, 0.28, 0.20],
    [8, 0.42, 0.30, 0.28],
    [9, 0.47, 0.29, 0.24],

    [10, 0.56, 0.24, 0.20],
    [11, 0.45, 0.26, 0.29],
    [12, 0.7, 0.18, 0.12],
    #[13, 0.464, 0.255, 0.281],
    #[14, 2.4, 55, 1.65],
]

number_of_matches = len(lst)


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

    df['1'] = df['home']
    df['X'] = df['draw']
    df['2'] = df['away']

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

    df['combination'] = df['combination'].apply(join_set)
    df['vakio_id'] = vakio_id
    df['list_index'] = list_index

    Combination.objects.filter(vakio_id=vakio_id, list_index=list_index).delete()
    df = df[['vakio_id', 'prob', 'combination', 'list_index']]
    data_dict = df.to_dict('records')
    instances = [Combination(**data) for data in data_dict]

    Combination.objects.bulk_create(instances)
