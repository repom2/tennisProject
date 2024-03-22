from vakio.task.moniveto.match_prob import match_probability
from vakio.task.moniveto.poisson import calculate_poisson
from vakio.task.moniveto.odds_from_stats import odds_from_stats
import logging
from vakio.models import Moniveto
from footballapi.models import BetFootball
from icehockeyapi.models import BetIceHockey
from django.utils import timezone
from datetime import datetime, timedelta
import unicodedata

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

# docker compose exec tennisproject poetry run python manage.py vakio moniveto
moniveto_id = 63432
list_index = 6

lst = [
        [0, 0.43, 0.29, 0.28, 'seriea'],
        [1, 0.8, 0.14, 0.06, 'laliga'],
        [2, 0.44, 0.27, 0.29, 'ligue1'],
        [3, 0.25, 0.3, 0.45, 'premier'],
    ]

matches_to_bet = len(lst)

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




    sport = 'hockey'
    sport = 'football'
    sport = None
    if sport == 'football':
        bet_table = BetFootball
    elif sport == 'hockey':
        bet_table = BetIceHockey
    else:
        print("sport not found!")
        pass
    if sport:
        lst = []
        try:
            home_name = unicodedata.normalize('NFKD', qs['home1']).encode('ASCII', 'ignore').decode('ASCII')
            away_name = unicodedata.normalize('NFKD', qs['away1']).encode('ASCII', 'ignore').decode('ASCII')
            probs1 = list(bet_table.objects.filter(
                home_name__icontains=home_name, away_name__icontains=away_name, start_at__gt=timezone.now() - timedelta(days=1)
            ).values_list('home_prob', 'draw_prob', 'away_prob', 'level').first())
        except TypeError:
            logging.info(f"No Match found: {qs['home1']} - {qs['away1']} ")
            probs1 = [0.4, 0.3, 0.3, 'liig']
        logging.info(f"{qs['home1']} - {qs['away1']} {probs1}")
        lst.append([0] + probs1)
        try:
            home_name = unicodedata.normalize('NFKD', qs['home2']).encode('ASCII',
                                                                          'ignore').decode(
                'ASCII')
            away_name = unicodedata.normalize('NFKD', qs['away2']).encode('ASCII',
                                                                          'ignore').decode(
                'ASCII')
            probs2 = list(bet_table.objects.filter(
                home_name__contains=home_name, away_name__contains=away_name
            ).values_list('home_prob', 'draw_prob', 'away_prob', 'level').first())
        except TypeError:
            logging.info(f"No Match found: {qs['home2']} - {qs['away2']} ")
            probs2 = [0.48, 0.26, 0.26, 'liig']
        logging.info(f"{qs['home2']} - {qs['away2']} {probs2}")
        lst.append([1] + probs2)
        try:
            home_name = unicodedata.normalize('NFKD', qs['home3']).encode('ASCII',
                                                                          'ignore').decode(
                'ASCII')
            away_name = unicodedata.normalize('NFKD', qs['away3']).encode('ASCII',
                                                                          'ignore').decode(
                'ASCII')
            probs3 = list(bet_table.objects.filter(
                home_name__contains=home_name, away_name__contains=away_name
            ).values_list('home_prob', 'draw_prob', 'away_prob', 'level').first())
        except TypeError:
            logging.info(f"No Match found: {qs['home3']} - {qs['away3']} ")
            probs3 = [0.79, 0.14, 0.7, 'liia']
        logging.info(f"{qs['home3']} - {qs['away3']} {probs3}")
        lst.append([2] + probs3)
        if qs['home4']:
            try:
                home_name = unicodedata.normalize('NFKD', qs['home4']).encode('ASCII',
                                                                              'ignore').decode(
                    'ASCII')
                away_name = unicodedata.normalize('NFKD', qs['away4']).encode('ASCII',
                                                                              'ignore').decode(
                    'ASCII')
                probs4 = list(bet_table.objects.filter(
                    home_name__contains=home_name, away_name__contains=away_name
                ).values_list('home_prob', 'draw_prob', 'away_prob', 'level').first())
            except TypeError:
                logging.info(f"No Match found: {qs['home4']} - {qs['away4']} ")
                probs4 = [0.37, 0.27, 0.36, 'liig']
            logging.info(f"{qs['home4']} - {qs['away4']} {probs4}")
            lst.append([3] + probs4)

    estimated_avg_goals = [
        [0, 3, 1.2],
        [1, 1.34, 1.67],
        [2, 1.17, 1.33],
        [3, 1.64, 1.94],
    ]

    lst = [
        [0, 0.43, 0.29, 0.28, 'seriea'],
        [1, 0.8, 0.14, 0.06, 'laliga'],
        [2, 0.44, 0.27, 0.29, 'ligue1'],
        [3, 0.25, 0.3, 0.45, 'premier'],
    ]
    is_using_own_data = True
    ice_hockey = False
    est_goals_from_prob = True
    if not is_using_own_data and not ice_hockey:
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
                sport,
            )
            print("---------------------------")
    if est_goals_from_prob:
        for i, item in enumerate(lst):
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
    else:
        for i, item in enumerate(estimated_avg_goals):
            #if i == 0 or i == 1:
             #   continue
            #estimated_avg_goals = match_probability(item[1], item[2], item[3])
            calculate_poisson(
                #estimated_avg_goals[0],
                estimated_avg_goals[i][1],
                #estimated_avg_goals[1],
                estimated_avg_goals[i][2],
                item[0],
                moniveto_id,
                list_index,
            )
            logging.info("Estimated avg goals: %s", estimated_avg_goals)
            print("---------------------------")