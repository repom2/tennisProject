from vakio.task.moniveto.match_prob import match_probability
from vakio.task.moniveto.poisson import calculate_poisson


lst = [
    [0, 2.05, 3.5, 4.2],
    [1, 3.64, 3.76, 2.05],
    [2, 2.8, 3.9, 2.47],
    #[3, 2.34, 4.25, 3.05],
]

goals = [
    [0, 16/11, 12/11, 11/10, 15/10, 'champ'],
    [1, 21/15, 9/15, 20/10, 10/10, 'champ'],
    [2, 20/11, 11/11, 23/14, 15/14, 'champ'],
    #[3, 41/18, 47/18, 40/19, 57/19, 'liiga'],
]
moniveto_id = 63229
list_index = 10


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
        try:
            estimated_avg_goals = estimated_avg_goals_calc(goals[i])
        except IndexError:
            exit()
        calculate_poisson(
            estimated_avg_goals[0],
            estimated_avg_goals[1],
            item[0],
            moniveto_id,
            list_index,
        )
        print("---------------------------")
