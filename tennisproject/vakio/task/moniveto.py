from vakio.task.match_prob import match_probability
from vakio.task.poisson import calculate_poisson


lst = [
    [0, 1.62, 4.2, 5.5],
    [1, 2.0, 3.6, 3.6],
    [2, 1.5, 4.33, 6.0],
    [3, 2.63, 3.5, 2.6],
]


def moniveto():
    for i in lst:
        estimated_avg_goals = match_probability(i[1], i[2], i[3])
        calculate_poisson(estimated_avg_goals[0], estimated_avg_goals[1], i[0])
