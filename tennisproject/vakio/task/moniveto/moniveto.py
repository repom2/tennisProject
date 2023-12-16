from vakio.task.moniveto.match_prob import match_probability
from vakio.task.moniveto.poisson import calculate_poisson

lst = [
    [0, 4.75, 4.3, 1.75],
    [1, 5.09, 3.2, 1.93],
    [2, 2.3, 3.2, 3.64],
    [3, 2.14, 3.96, 3.27],
]

goals = [
    [0, 10/7, 9/7, 17/8, 12/8, 'pl'],
    [1, 10/7, 9/7, 9/7, 5/7, 'ita'],
    [2, 10/8, 22/16, 6/8, 12/8, 'esp'],
    [3, 9/7, 9/7, 13/7, 20/7, 'ger'],
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
    if i[5] == 'pl':
        goals_home = premier_avg_goals_home
        conceded_home = premier_avg_conceded_home
    elif i[5] == 'ita':
        goals_home = seria_avg_goals_home
        conceded_home = seria_avg_conceded_home
    elif i[5] == 'esp':
        goals_home = laliga_avg_goals_home
        conceded_home = laliga_avg_conceded_home
    elif i[5] == 'ger':
        goals_home = bundes_avg_goals_home
        conceded_home = bundes_avg_conceded_home
    else:
        goals_home = liiga_avg_goals_home
        conceded_home = liiga_avg_conceded_home

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
        try:
            estimated_avg_goals = estimated_avg_goals_calc(goals[i])
        except IndexError:
            exit()
        calculate_poisson(estimated_avg_goals[0], estimated_avg_goals[1], item[0])
        print("---------------------------")
