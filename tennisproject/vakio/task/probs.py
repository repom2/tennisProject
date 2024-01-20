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

list_index = 7
vakio_id = 55505
lst = [
    [1, 1/0.36, 1/0.34, 1/0.3],
    [2, 1.72, 3.55, 6.25],
    [3, 1.65, 3.9, 6.1],

    [4, 1.87, 3.71, 4.42],
    [5, 3.1, 3.7, 2.3],
    [6, 1.55, 4.4, 6.21],

    [7, 1.145, 9.0, 20.0],
    [8, 2.23, 3.0, 4.11],
    [9, 3.57, 3.36, 2.22],

    [10, 1/0.23, 1/0.28, 1/0.49],
    [11, 2.11, 3.04, 4.34],
    [12, 1/0.41, 1/0.33, 1/0.27],
    #[13, 3.56, 4.29, 1.92],
    #[14, 2.4, 55, 1.65],
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

    df['combination'] = df['combination'].apply(join_set)
    df['vakio_id'] = vakio_id
    df['list_index'] = list_index

    Combination.objects.filter(vakio_id=vakio_id, list_index=list_index).delete()
    df = df[['vakio_id', 'prob', 'combination', 'list_index']]
    data_dict = df.to_dict('records')
    instances = [Combination(**data) for data in data_dict]

    Combination.objects.bulk_create(instances)
