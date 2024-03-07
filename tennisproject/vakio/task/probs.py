import pandas as pd
import itertools
from vakio.models import Combination
import os
from multiprocessing import Pool

"""
    13 kohdetta oikein 26 %
    12 kohdetta oikein 13 %
    11 kohdetta oikein 9 %
    10 kohdetta oikein 15 %.
"""

list_index = 6
vakio_id = 55551

lst = [
    [1, 0.15, 0.25, 0.60],
    [2, 0.1, 0.19, 0.71],
    [3, 0.55, 0.25, 0.2],

    [4, 0.35, 0.3, 0.35],
    [5, 0.55, 0.25, 0.20],
    [6, 0.71, 0.19, 0.1],

    [7, 0.62, 0.21, 0.17],
    [8, 0.2, 0.25, 0.55],
    [9, 0.27, 0.28, 0.45],

    [10, 0.32, 0.28, 0.40],
    [11, 0.6, 0.25, 0.15],
    [12, 0.45, 0.29, 0.26],

    [13, 0.15, 0.25, 0.60],
    [14, 0.45, 0.29, 0.26],
    [15, 0.4, 0.29, 0.31],
]

number_of_matches = len(lst)


def arbitrage_check(i):
    if(1 / i[1] + 1 / i[2] + 1 / i[3]) < 1:
        print("Arbitage found!")


def join_set(s):
    return ''.join(s)


def process_combination(combo):
    if combo[0] != '1' and combo[1] == '1':
        return calculate_prob(combo, df)
    return None


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

    combination_list = []
    probabilities = []
    for combo in combinations:
        if combo[0] != '2' and combo[1] == '2' and combo[2] == '1':
            prob = calculate_prob(combo, df)
            probabilities.append(prob)
            combination_list.append(combo)

    print('Number of combination_list: ', len(combination_list))

    # probabilities = [calculate_prob(combo, df) for combo in combinations
                     #if combo[5] == '1' and combo[4] != '2' and combo[2] != '2' and combo[1] != '1']

    print('Number of probabilities: ', len(probabilities))
    df = pd.DataFrame({
        "prob": probabilities,
        "combination": combination_list,
    })

    df['combination'] = df['combination'].apply(join_set)
    df['vakio_id'] = vakio_id
    df['list_index'] = list_index

    Combination.objects.filter(vakio_id=vakio_id, list_index=list_index).delete()
    df = df[['vakio_id', 'prob', 'combination', 'list_index']]
    data_dict = df.to_dict('records')
    instances = [Combination(**data) for data in data_dict]

    Combination.objects.bulk_create(instances)
