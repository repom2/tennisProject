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

list_index = 1
vakio_id = 100437

lst = [
    [1, 0.745, 0.159, 0.096],
    [2, 0.1, 0.17, 0.73],
    [3, 0.646, 0.194, 0.16],

    [4, 0.341, 0.243, 0.416],
    [5, 0.566, 0.219, 0.216],
    [6, 0.405, 0.242, 0.353],

    [7, 0.624, 0.202, 0.174],
    [8, 0.261, 0.272, 0.467],
    [9, 0.318, 0.281, 0.4],

    [10, 0.418, 0.248, 0.334],
    [11, 0.489, 0.243, 0.267],
    [12, 0.312, 0.267, 0.421],
    [13, 0.346, 0.274, 0.381],
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
