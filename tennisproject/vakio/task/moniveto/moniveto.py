from vakio.task.moniveto.match_prob import match_probability
from vakio.task.moniveto.poisson import calculate_poisson
from vakio.task.moniveto.odds_from_stats import odds_from_stats
import logging
from vakio.models import Moniveto
from footballapi.models import BetFootball
from django.utils import timezone

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

moniveto_id = 63330
list_index = 1

lst = [
    [0, 0.2, 0.254, 0.546, 'seriea'],
    [1, 0.531, 0.243, 0.227, 'laliga'],
    [2,  0.419, 0.266, 0.314, 'ligue1'],
    #[3, 0.745, 0.159, 0.096, 'premier'],
]

matches_to_bet = len(lst)

estimated_avg_goals = [
    [0, 2.6, 2.3],
    [1, 2.3, 2.6],
    [2, 2.51, 2.8],
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

def moniveto():
    qs = Moniveto.objects.filter(moniveto_id=moniveto_id, list_index=list_index).values(
        'home1', 'away1', 'home2', 'away2', 'home3', 'away3', 'home4', 'away4',
    ).first()

    lst = []
    logging.info(qs)
    probs1 = list(BetFootball.objects.filter(
        home_name__contains=qs['home1'], away_name__contains=qs['away1'], start_at__gt=timezone.now()
    ).values_list('home_prob', 'draw_prob', 'away_prob', 'level').first())
    logging.info(probs1)
    lst.append([0] + probs1)
    probs2 = list(BetFootball.objects.filter(
        home_name__contains=qs['home2'], away_name__contains=qs['away2']
    ).values_list('home_prob', 'draw_prob', 'away_prob', 'level').first())
    logging.info(probs2)
    lst.append([1] + probs2)
    try:
        probs3 = list(BetFootball.objects.filter(
            home_name__contains=qs['home3'], away_name__contains=qs['away3']
        ).values_list('home_prob', 'draw_prob', 'away_prob', 'level').first())
    except TypeError:
        probs3 = [0.08, 0.18, 0.74, 'laliga']
    logging.info(probs3)
    lst.append([2] + probs3)
    if qs['home4']:
        probs4 = list(BetFootball.objects.filter(
            home_name__contains=qs['home4'], away_name__contains=qs['away4']
        ).values_list('home_prob', 'draw_prob', 'away_prob').first())
        logging.info(probs4)
        lst.append([3] + probs4)

    estimated_avg_goals = [
        [0, 2.6, 2.3],
        [1, 2.3, 2.6],
        [2, 2.51, 2.8],
        # [3, 2.1, 1.0],
    ]
    is_using_own_data = True
    ice_hockey = True
    if is_using_own_data and not ice_hockey:
        for i, item in enumerate(lst):
            arbitrage_check(item)
            estimated_goals = estimated_avg_goals_calc(goals[i])
            logging.info( estimated_goals)
            calculate_poisson(
                estimated_avg_goals[i][1],
                #estimated_goals[1],
                estimated_avg_goals[i][2],
                #estimated_goals[2],
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