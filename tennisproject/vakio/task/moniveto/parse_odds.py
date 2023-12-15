from vakio.task.moniveto.match1 import get_match1
from vakio.task.moniveto.match2 import get_match2
from vakio.task.moniveto.match3 import get_match3
from vakio.task.moniveto.match4 import get_match4
import logging
from vakio.models import MonivetoProb

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

def get_prob_sum(match_list, match_nro, multiplier=1):
    prob_sum = 0
    for index in range(0, len(match_list), 2):
        i, j = match_list[index].split(":")
        i = i.strip()
        j = j.strip()
        id = f"{match_nro}-{i}-{j}"
        score = f"{i}-{j}"
        prob = (1 / float(match_list[index + 1])) * multiplier
        logging.info("id: %s" % id)
        logging.info("score: %s" % score)
        logging.info("prob: %s" % prob)
        prob_sum += prob
        MonivetoProb.objects.update_or_create(
            id=f"{match_nro}-{i}-{j}",
            defaults={
                "match_nro": match_nro,
                "score": f"{i}-{j}",
                "prob": prob,
            }
        )
    logging.info("prob_sum: %s" % prob_sum)
    percent = (prob_sum - 1)
    logging.info("percent: %s" % percent)


def parse_odds():
    MonivetoProb.objects.all().delete()
    match1 = get_match1().split("\n")
    get_prob_sum(match1, 0, multiplier=0.61)
    match2 = get_match2().split("\n")
    get_prob_sum(match2, 1, multiplier=0.61)
    match3 = get_match3().split("\n")
    get_prob_sum(match3, 2, multiplier=0.61)
    match4 = get_match4().split("\n")
    get_prob_sum(match4, 3, multiplier=0.61)

