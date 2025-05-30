from vakio.task.moniveto.match_prob import match_probability
from vakio.task.moniveto.poisson import calculate_poisson, calculate_poisson_football
from vakio.task.moniveto.odds_from_stats import odds_from_stats
from vakio.task.moniveto.calc_probs import calc_probs
import logging
from vakio.models import Moniveto

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

lst = [
        [0, 0.52, 0.27, 0.21, 'seriea'],
        [1, 0.52, 0.27, 0.21, 'laliga'],
        [2, 0.44, 0.28, 0.28, 'ligue1'],
        [3, 0.25, 0.3, 0.45, 'premier'],
    ]

matches_to_bet = len(lst)

goals = [
    [0, 30/11, 14/11, 14/11, 10/11, 'esp'],
    [1, 13/10, 6/10, 13/11, 22/11, 'ita'],
    [2, 7/4, 6/8, 11/8, 3/4, 'ita'],
    [3, 73/23, 52/23, 68/24, 57/24, 'liiga'],
]


def arbitrage_check(i):
    print(round(1 / i[1], 2), round(1 / i[2], 2), round(1 / i[3], 2))
    if(1 / i[1] + 1 / i[2] + 1 / i[3]) < 1:
        print("Arbitage found!")


def estimated_avg_goals_calc(i):
    premier_avg_goals_home = 1.74
    premier_avg_conceded_home = 1.38
    seria_avg_goals_home = 1.43
    seria_avg_conceded_home = 1.15
    laliga_avg_goals_home = 1.51
    laliga_avg_conceded_home = 1.2
    bundes_avg_goals_home = 1.98
    bundes_avg_conceded_home = 1.44
    liiga_avg_goals_home = 2.66
    liiga_avg_conceded_home = 2.3
    mestis_avg_goals_home = 3.35
    mestis_avg_conceded_home = 2.98
    ligue1_avg_goals_home = 1.45
    ligue1_avg_conceded_home = 1.06
    championship_avg_goals_home = 1.51
    championship_avg_conceded_home = 1.24
    if i[5] == 'pl':
        goals_home = premier_avg_goals_home
        conceded_home = premier_avg_conceded_home
    elif i[5] == 'champ':
        goals_home = championship_avg_goals_home
        conceded_home = championship_avg_conceded_home
    elif i[5] == 'ita':
        goals_home = seria_avg_goals_home
        conceded_home = seria_avg_conceded_home
    elif i[5] == 'esp':
        goals_home = laliga_avg_goals_home
        conceded_home = laliga_avg_conceded_home
    elif i[5] == 'ger':
        goals_home = bundes_avg_goals_home
        conceded_home = bundes_avg_conceded_home
    elif i[5] == 'mestis':
        goals_home = mestis_avg_goals_home
        conceded_home = mestis_avg_conceded_home
    elif i[5] == 'fra':
        goals_home = ligue1_avg_goals_home
        conceded_home = ligue1_avg_conceded_home
    elif i[5] == 'liiga':
        goals_home = liiga_avg_goals_home
        conceded_home = liiga_avg_conceded_home
    else:
        print("League not found!")
        exit()

    home = i[1] / goals_home
    home_defence = i[2] / conceded_home

    away = i[3] / conceded_home
    away_defence = i[4] / goals_home

    home = home * away_defence * goals_home
    away = away * home_defence * conceded_home

    return ['estimated_goals', home, away]


def moniveto(list_index, moniveto_id):
    qs = Moniveto.objects.filter(moniveto_id=moniveto_id, list_index=list_index).values(
        'home1', 'away1', 'home2', 'away2', 'home3', 'away3', 'home4', 'away4',
    ).first()

    sport = 'footbal'

    #calc_probs(qs, sport)

    estimated_avg_goals = [
        [0, 1.3, 5.8],
        [1, 3.1, 2.15],
        [2, 5.375, 1.3],
        [3, 4.6, 1.5],
    ]

    lst = [
        [0, 1.13, 10.5, 22.8, 'seriea'],
        [1, 1.75, 3.7, 6.5, 'laliga'],
        [2, 3.0, 3.8, 2.3, 'ligue1'],
        [3, 110.95, 55.55, 1.041, 'premier'],
    ]
    # divie all values in list of item by 1
    for i, item in enumerate(lst):
        lst[i] = [item[0], 1/ item[1], 1 / item[2], 1 / item[3], item[4]]
    is_using_own_data = False
    ice_hockey = False
    est_goals_from_prob = True
    last = True
    use_estimated_avg_goals = True
    if use_estimated_avg_goals:
        for i, item in enumerate(lst):
            arbitrage_check(item)
            if sport == 'football':
                calculate_poisson_football(
                    estimated_avg_goals[i][1],
                    estimated_avg_goals[i][2],
                    item[0],
                    moniveto_id,
                    list_index,
                )
            else:
                calculate_poisson(
                    estimated_avg_goals[i][1],
                    estimated_avg_goals[i][2],
                    item[0],
                    moniveto_id,
                    list_index,
                )
            print("---------------------------")
    elif ice_hockey:
        for i, item in enumerate(lst):
            odds_from_stats(
                item[0],
                moniveto_id,
                list_index,
                item[1],
                item[2],
                item[3],
                item[4],
                sport,
            )
            print("---------------------------")
    elif est_goals_from_prob:
        for i, item in enumerate(lst):
            estimated_avg_goals = match_probability(item[1], item[2], item[3])
            calculate_poisson_football(
            #calculate_poisson(
                estimated_avg_goals[0],
                estimated_avg_goals[1],
                item[0],
                moniveto_id,
                list_index,
            )
            logging.info("Estimated avg goals: %s", estimated_avg_goals)
            print("---------------------------")
    else:
        logging.info("Using own data")
        for i, item in enumerate(estimated_avg_goals):
            calculate_poisson(
                estimated_avg_goals[i][1],
                estimated_avg_goals[i][2],
                item[0],
                moniveto_id,
                list_index,
            )
            logging.info("Estimated avg goals: %s", estimated_avg_goals[i])
            print("---------------------------")