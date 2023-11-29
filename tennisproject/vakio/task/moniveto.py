from vakio.task.match_prob import match_probability
from vakio.task.poisson import calculate_poisson


lst = [
    [0, 1.75, 4.2, 4.0],
    [1, 1.36, 5.0, 8.0],
    [2, 1.22, 7.0, 11],
    [3, 2.55, 3.4, 2.7],
]


def moniveto():
    for i in lst:
        estimated_avg_goals = match_probability(i[1], i[2], i[3])
        calculate_poisson(estimated_avg_goals[0], estimated_avg_goals[1], i[0])
