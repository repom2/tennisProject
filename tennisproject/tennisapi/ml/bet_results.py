from tennisapi.models import BetWta
import logging
from tabulate import tabulate

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

def home_draw_bet(bet, bankroll):
    yield_h = bet.home_yield
    yield_d = bet.draw_yield
    total_bet = 0.05 * bankroll

    total_yield = yield_h + yield_d

    proportion_h = yield_h / total_yield
    proportion_d = yield_d / total_yield

    bet_h = total_bet * proportion_h
    bet_d = total_bet * proportion_d

    print(f"Bet on Home: {bet_h:.2f}")
    print(f"Bet on Draw: {bet_d:.2f}")
    return bet_h, bet_d


def away_draw_bet(bet, bankroll):
    yield_a = bet.away_yield
    yield_d = bet.draw_yield
    total_bet = 0.05 * bankroll

    total_yield = yield_a + yield_d

    proportion_a = yield_a / total_yield
    proportion_d = yield_d / total_yield

    bet_a = total_bet * proportion_a
    bet_d = total_bet * proportion_d

    print(f"Bet on Away: {bet_a:.2f}")
    print(f"Bet on Draw: {bet_d:.2f}")
    return bet_a, bet_d


def home_away_bet(bet, bankroll):
    yield_a = bet.away_yield
    yield_h = bet.home_yield


    total_yield = yield_a + yield_h
    total_bet = 0.05 * bankroll

    proportion_a = yield_a / total_yield
    proportion_h = yield_h / total_yield

    bet_a = total_bet * proportion_a
    bet_h = total_bet * proportion_h

    print(f"Bet on Home: {bet_h:.2f}")
    print(f"Bet on Away: {bet_a:.2f}")
    return bet_h, bet_a

def bet_results():
    qs = BetWta.objects.all().order_by('start_at')
    bankroll = 1000
    use = 'yield'
    bet_count = 0
    match_count = 0
    for bet in qs:
        outcome = bet.match.winner_code
        if outcome == None:
            continue
        logging.info(bet.start_at)
        logging.info(str(outcome) + ': ' + str(bet.match.home_score) + ' - ' + str(bet.match.away_score))
        logging.info(bet.home_name + ' vs ' + bet.away_name + ' ' + bet.match.id + ' ' + str(bet.match.match_num) + ' ' + str(bet.match.round_name))
        try:
            home_odds = float(bet.match.home_odds)
            away_odds = float(bet.match.away_odds)
        except TypeError:
            continue
        logging.info(str(home_odds) + ' ' + str(away_odds))
        logging.info(str(bet.home_yield) + ' ' + str(bet.away_yield))

        if bet.home_yield is None or bet.away_yield is None or home_odds is None or away_odds is None:
            continue
        if use == 'elo_prob':
            if bet.elo_prob is None:
                continue
            home_yield = home_odds * bet.elo_prob
            away_yield = away_odds * (1 - bet.elo_prob)
        elif use == 'year_elo_prob':
            if bet.year_elo_prob is None:
                continue
            home_yield = home_odds * bet.year_elo_prob
            away_yield = away_odds * (1 - bet.year_elo_prob)
        elif use == 'stats_win':
            if bet.stats_win is None:
                continue
            home_yield = home_odds * bet.stats_win
            away_yield = away_odds * (1 - bet.stats_win)
        elif use == 'common_opponents':
            if bet.common_opponents is None or bet.common_opponents_count < 9:
                continue
            home_yield = home_odds * bet.common_opponents
            away_yield = away_odds * (1 - bet.common_opponents)
        elif use == 'yield':
            home_yield = bet.home_yield
            away_yield = bet.away_yield
        bets = []
        total_yield = 0
        match_count += 1
        if home_yield > 1.0:# and home_odds > 1.89:
            bets.append('1')
            total_yield += home_yield
        if away_yield > 1.0:# and away_odds > 1.89:
            bets.append('2')
            total_yield += away_yield
        logging.info(bets)

        if '1' in bets:
            bet_count += 1
            home_bet = (home_yield -1) / (home_odds - 1) * bankroll
            if bankroll * 0.05 < home_bet:
                home_bet = bankroll * 0.05
            if outcome == 1:
                win = home_bet * (home_odds-1)
                bankroll += win
            else:
                bankroll -= home_bet
        elif '2' in bets:
            bet_count += 1
            away_bet = (away_yield -1) / (away_odds - 1) * bankroll
            if bankroll * 0.05 < away_bet:
                away_bet = bankroll * 0.05
            if outcome == 2:
                win = away_bet * (away_odds-1)
                bankroll += win
            else:
                bankroll -= away_bet
        else:
            logging.info('No bets')
        logging.info(bankroll)
        # conitnue loop when pressing enter
        #input("Press Enter to continue...")
    logging.info(bankroll)
    logging.info(bet_count)
    logging.info(match_count)


"""In SQL
select sum(win), sum(case when bet != 0 then 1 else 0 end), count(*) from (
select
	date(start_at),
	home_odds,
	away_odds,
	case
	when bet = 1 and winner_code = 1 then (home_odds -1 ) * 100
	when bet = 2 and winner_code = 2 then (away_odds -1 ) * 100
	when bet = 1 and winner_code = 2 then -100
	when bet = 2 and winner_code = 1 then -100
	else 0 end win,
	bet,
	winner_code,
	home_yield,
	away_yield
from (
select
	case when home_yield > 1 then 1 when away_yield > 1 then 2 else 0 end bet,
	home_odds,
	away_odds,
	winner_code,
	start_at,
	home_yield,
	away_yield
from (
select start_at, home_odds, away_odds, stats_win * home_odds as home_yield, (1 - stats_win) * away_odds as away_yield, winner_code from (
select a.start_at, elo_prob_hard stats_win, a.surface, b.home_name, b.away_name, winner_code,b.home_odds, b.away_odds, elo_prob_hard from tennisapi_betwta b
inner join tennisapi_wtamatch a on a.id=b.match_id
where b.home_odds is not null
and a.surface ilike '%hard%'
order by a.start_at
) s
) bet
) win
) results;
"""