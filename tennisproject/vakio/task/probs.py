import pandas as pd
import itertools
from vakio.models import Combination
import os
from multiprocessing import Pool
from vakio import vakio

"""
    13 kohdetta oikein 26 %
    12 kohdetta oikein 13 %
    11 kohdetta oikein 9 %
    10 kohdetta oikein 15 %.
"""

list_index = vakio.list_index
vakio_id = vakio.vakio_id

lst = vakio.lst

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
        #if combo[0] != '2' and combo[1] == '2' and combo[2] == '1':
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
