import logging

from vakio.task.moniveto.poisson import (
    calculate_poisson,
    calculate_poisson_football
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)


def moniveto(list_index, moniveto_id):
    sport = "football"

    estimated_avg_goals = [
        [0, 3.2, 0.45],
        [1, 0.5, 3.0],
        [2, 2.05, 0.75],
        [3, 1.5, 1.05],
    ]

    for i, item in enumerate(estimated_avg_goals):
        if sport == "football":
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
