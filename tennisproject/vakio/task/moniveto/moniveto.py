from vakio.task.moniveto.match_prob import match_probability
from vakio.task.moniveto.poisson import calculate_poisson

lst = [
    [0, 1.943, 4.45, 3.5],
    [1, 3.04, 4.35, 2.19],
    [2, 2.4, 4.0, 2.75],
    [3, 2.27, 4.0, 3.05],
]

goals = [
    [0, 3.214, 3.07, 2.46, 2.933],
    [1, 44/14, 36/14, 39/14, 30/14],
    [2, 35/14, 31/14, 33/15, 39/15],
    [3, 35/14, 30/14, 37/15, 42/15],
]


def arbitrage_check(i):
    print(round(1 / i[1], 2), round(1 / i[2], 2), round(1 / i[3], 2))
    if(1 / i[1] + 1 / i[2] + 1 / i[3]) < 1:
        print("Arbitage found!")


def estimated_avg_goals_calc(i):
    liiga_avg_goals_home = 2.82
    liiga_avg_conceded_home = 2.54

    home = liiga_avg_goals_home + (i[1] - liiga_avg_goals_home) + (i[4] - liiga_avg_goals_home)

    away = liiga_avg_conceded_home + (i[3] - liiga_avg_conceded_home) + (
                i[2] - liiga_avg_conceded_home)
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
