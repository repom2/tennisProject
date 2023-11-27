import pandas as pd
import itertools
from vakio.models import Combination
import os

lst =[
    [1, 2.75, 51, 1.5],
    [2, 2.05, 51, 1.8],
    [3, 2.15, 41, 1.74],
    [4, 2.1, 51, 1.76],
    [5, 1.68, 51, 2.25],
    [6, 2.3, 51, 1.66],
    [7, 1.8, 51, 2.05],
    [8, 4.75, 51, 1.2],
    [9, 1.68, 51, 2.25],
    [10, 2.45, 51, 1.6],
    #[11, 1.91, 3.8, 3.8],
    #[12, 3.0, 3.25, 2.45],
]


def join_set(s):
    return ''.join(s)


# Function to calculate probability
def calculate_prob(combination, df):
    p = 1
    for i, outcome in enumerate(combination):
        p *= df.loc[i, outcome]
    return round(p,8)


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

    df['combination'] = df['combination'].apply(join_set)

    for index, row in df.iterrows():
        print(row)
        print(row["combination"])
        print(type(row["combination"]))
        Combination.objects.update_or_create(
            id=row["combination"],
            defaults={
                "prob": row["prob"],
            }
        )
