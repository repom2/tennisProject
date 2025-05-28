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
        [0, 1.3475, 1.775],
        [1, 2.3, 0.9],
        [2, 1.65, 1.3],
        #[3, 1.0, 2.1],
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
