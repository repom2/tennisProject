from footballapi.models import BetFootball
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
    qs = BetFootball.objects.all().order_by('start_at')
    bankroll = 1000
    bet_count = 0
    for bet in qs:
        outcome = bet.match.winner_code
        if outcome == None:
            continue
        logging.info(bet.start_at)
        logging.info(str(outcome) + ': ' + str(bet.match.home_score) + ' - ' + str(bet.match.away_score))
        logging.info(bet.home_name + ' vs ' + bet.away_name + ' ' + bet.match.id)
        logging.info(str(bet.home_odds) + ' ' + str(bet.draw_odds) + ' ' + str(bet.away_odds))
        logging.info(str(bet.home_yield) + ' ' + str(bet.draw_yield) + ' ' + str(bet.away_yield))
        bets = []
        total_yield = 0
        if bet.home_yield > 1.05:
            bets.append('1')
            total_yield += bet.home_yield
        if bet.draw_yield > 1.05:
            bets.append('X')
            total_yield += bet.draw_yield
        if bet.away_yield > 1.05:
            bets.append('2')
            total_yield += bet.away_yield
        logging.info(bets)
        if len(bets) > 0:
            bet_count += 1
        if '1' in bets and 'X' in bets:
            home_bet, draw_bet = home_draw_bet(bet, bankroll)
            if outcome == 1:
                win = home_bet * (bet.home_odds-1)
                bankroll += win - draw_bet
            elif outcome == 3:
                win = draw_bet * (bet.draw_odds-1)
                bankroll += win - home_bet
            elif outcome == 2:
                bankroll -= home_bet + draw_bet
            else:
                continue
        elif '2' in bets and 'X' in bets:
            away_bet, draw_bet = home_draw_bet(bet, bankroll)
            if outcome == 2:
                win = away_bet * (bet.away_odds-1)
                bankroll += win - draw_bet
            elif outcome == 3:
                win = draw_bet * (bet.draw_odds-1)
                bankroll += win - away_bet
            elif outcome == 1:
                bankroll -= away_bet + draw_bet
            else:
                continue
        elif '2' in bets and '1' in bets:
            home_bet, away_bet = home_draw_bet(bet, bankroll)
            if outcome == 2:
                win = away_bet * (bet.away_odds-1)
                bankroll += win - home_bet
            elif outcome == 1:
                win = home_bet * (bet.home_odds-1)
                bankroll += win - away_bet
            elif outcome == 3:
                bankroll -= away_bet + home_bet
            else:
                continue
        elif '1' in bets and '2' not in bets and 'X' not in bets:
            home_bet = (bet.home_yield -1) / (bet.home_odds - 1) * bankroll
            if bankroll * 0.05 < home_bet:
                home_bet = bankroll * 0.05
            if outcome == 1:
                win = home_bet * (bet.home_odds-1)
                bankroll += win
            else:
                bankroll -= home_bet
        elif '2' in bets and '1' not in bets and 'X' not in bets:
            away_bet = (bet.away_yield -1) / (bet.away_odds - 1) * bankroll
            if bankroll * 0.05 < away_bet:
                away_bet = bankroll * 0.05
            if outcome == 2:
                win = away_bet * (bet.away_odds-1)
                bankroll += win
            else:
                bankroll -= away_bet
        elif 'X' in bets and '1' not in bets and '2' not in bets:
            draw_bet = (bet.draw_yield -1) / (bet.draw_odds - 1) * bankroll
            if bankroll * 0.05 < draw_bet:
                draw_bet = bankroll * 0.05
            if outcome == 3:
                win = draw_bet * (bet.draw_odds-1)
                bankroll += win
            else:
                bankroll -= draw_bet
        logging.info(bankroll)
        # conitnue loop when pressing enter
        #input("Press Enter to continue...")
    logging.info(bankroll)
    logging.info(bet_count)