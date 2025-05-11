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
    sport = "footbal"

    estimated_avg_goals = [
        [0, 4.1, 1.3],
        [1, 1.55, 4.45],
        #[2, 1.9, 0.95],
        #[3, 1.55, 4.45],
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
