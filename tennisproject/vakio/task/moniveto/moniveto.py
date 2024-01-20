from vakio.task.moniveto.match_prob import match_probability
from vakio.task.moniveto.poisson import calculate_poisson


moniveto_id = 63235
list_index = 5

lst = [
    [0, 2.0, 3.6, 3.0],
    [1, 1.65, 3.9, 6.1],
    [2, 1.72, 3.55, 6.25],
    [3, 1.87, 3.71, 4.42],
]
estimated_avg_goals = [
    [0, 2.1, 2.3],
    [1, 1.75, 0.75],
    [2, 1.65, 0.76],
    [2, 1.7, 1.23],
]

goals = [
    [0, 16/10, 11/10, 12/10, 11/10, 'ita'],
    [1, 21/10, 11/10, 15/10, 7/10, 'esp'],
    [2, 14/10, 11/10, 9/10, 14/10, 'pl'],
    #[3, 41/18, 47/18, 40/19, 57/19, 'liiga'],
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

    home = goals_home + (i[1] - goals_home) + (i[4] - goals_home)

    away = conceded_home + (i[3] - conceded_home) + (
                i[2] - conceded_home)
    print(round(home, 2), round(away, 2))
    return [home, away]

def moniveto():

    for i, item in enumerate(lst):
        #estimated_avg_goals = match_probability(i[1], i[2], i[3])
        #calculate_poisson(estimated_avg_goals[0], estimated_avg_goals[1], i[0])
        #estimated_avg_goals = [3.1, 2.54]
        arbitrage_check(item)
        # try:
            # estimated_avg_goals = estimated_avg_goals_calc(goals[i])
        # except IndexError:
            # exit()
        calculate_poisson(
            estimated_avg_goals[i][1],
            estimated_avg_goals[i][2],
            item[0],
            moniveto_id,
            list_index,
        )
        print("---------------------------")
