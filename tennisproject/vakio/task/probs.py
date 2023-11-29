import pandas as pd
import itertools
from vakio.models import Combination
import os

lst = [
    [1, 1.75, 4.2, 4.0],
    [2, 1.36, 5.0, 8.0],
    [3, 1.22, 7.0, 11.0],
    [4, 2.55, 3.4, 2.7],
    [5, 1.4, 4.5, 8.0],
    [6, 2.0, 3.75, 3.5],
    [7, 1.65, 4.0, 5.0],
    [8, 1.33, 5.5, 9.0],
    [9, 6.0, 4.2, 1.55],
    [10, 1.73, 4.0, 4.33],
    [11, 1.6, 4.2, 5.25],
    [12, 1.45, 4.5, 7.0],
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
    max_win = 100000
    limit = 1 / (max_win / cost)
    df = pd.DataFrame(lst, columns=['line', 'home', 'draw', 'away'])
    df['1%'] = 1 / df['home']
    df['x%'] = 1 / df['draw']
    df['2%'] = 1 / df['away']
    df['%'] = 1 - (df['x%'] + df['2%'] + df['1%'] - 1)
    df['1'] = df['%'] * df['1%']
    df['2'] = df['%'] * df['2%']
    df['x'] = df['%'] * df['x%']

    outcomes = ['1', 'x', '2']

    # Generate all possible combinations for 12 matches
    combinations = list(itertools.product(outcomes, repeat=len(df)))

    print('Number of combinations: ', len(combinations))

    probabilities = [calculate_prob(combo, df) for combo in combinations]

    df = pd.DataFrame({
        "prob": probabilities,
        "combination": combinations,
    })

    print('Number of combinations with probability ', limit, len(df))

    df['id'] = df['combination'].apply(join_set)

    Combination.objects.all().delete()
    df = df[['id', 'prob']]
    data_dict = df.to_dict('records')
    instances = [Combination(**data) for data in data_dict]

    Combination.objects.bulk_create(instances)
