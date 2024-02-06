from vakio.task.moniveto.match_prob import match_probability
from vakio.task.moniveto.poisson import calculate_poisson
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

moniveto_id = 63290
list_index = 1

lst = [
    [0, 0.503, 0.233, 0.264],
    [1, 0.332, 0.281, 0.387],
    [2, 0.626, 0.198, 0.176],
    #[3, 0.572, 0.209, 0.219],
]

matches_to_bet = len(lst)

estimated_avg_goals = [
    [0, 1.9, 2.8],
    [1, 2.51, 2.833],
    #[2, 2.51, 2.8],
    #[3, 2.1, 1.0],
]

goals = [
    [0, 30/11, 14/11, 14/11, 10/11, 'esp'],
    [1, 13/10, 6/10, 13/11, 22/11, 'ita'],
    [2, 7/4, 6/8, 11/8, 3/4, 'ita'],
    #[3, 73/23, 52/23, 68/24, 57/24, 'liiga'],
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
    liiga_avg_goals_home = 2.82
    liiga_avg_conceded_home = 2.54
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

def moniveto():
    estimated_avg_goals = [
        [0, 1.9, 2.8],
        [1, 2.51, 2.833],
        [2, 2.51, 2.8],
        # [3, 2.1, 1.0],
    ]
    is_using_own_data = False
    if is_using_own_data:
        for i, item in enumerate(lst):
            arbitrage_check(item)
            estimated_goals = estimated_avg_goals_calc(goals[i])
            logging.info( estimated_goals)
            calculate_poisson(
                #estimated_avg_goals[i][1],
                estimated_goals[1],
                #estimated_avg_goals[i][2],
                estimated_goals[2],
                item[0],
                moniveto_id,
                list_index,
            )
            print("---------------------------")
    else:
        for i, item in enumerate(lst):
            #if i == 0 or i == 1:
             #   continue
            estimated_avg_goals = match_probability(item[1], item[2], item[3])
            calculate_poisson(
                estimated_avg_goals[0],
                estimated_avg_goals[1],
                item[0],
                moniveto_id,
                list_index,
            )
            logging.info("Estimated avg goals: %s", estimated_avg_goals)
            print("---------------------------")