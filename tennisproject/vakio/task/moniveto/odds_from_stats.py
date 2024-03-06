from icehockeyapi.models import Liiga
from footballapi.models import PremierLeague, LaLiga, Bundesliga, SerieA, Ligue1, Championship, AllLeagues
from django.db.models import Value, CharField
from django.db.models.functions import Concat, Cast
from django.db.models import Count, Case, When, Value, F, FloatField, TextField
from vakio.models import MonivetoProb
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

def odds_from_stats(
        match_nro,
        moniveto_id,
        list_index,
        home_win,
        draw,
        away_win,
        league,
        sport,
):
    if sport == 'hockey':
        league =  Liiga
    else:
        league = AllLeagues

    qs = league.objects.filter(
        home_score__isnull=False,
        away_score__isnull=False
    )

    predictions_qs  = qs.annotate(
        outcome=Case(
            When(home_score__gt=F('away_score'), then=Value('home_win')),
            When(home_score=F('away_score'), then=Value('draw')),
            When(home_score__lt=F('away_score'), then=Value('away_win')),
            output_field=TextField()
        ))

    # Calculate original totals (this needs to be done in Python since Django ORM does not support dynamic aggregation based on annotated values)
    original_totals = {
        'home_win': predictions_qs.filter(outcome='home_win').count() / predictions_qs.count(),
        'draw': predictions_qs.filter(outcome='draw').count() / predictions_qs.count(),
        'away_win': predictions_qs.filter(outcome='away_win').count() / predictions_qs.count(),
    }
    logging.info(f"Total matches: {qs.count()}, {league}, Original totals: {original_totals['home_win']:.2f}, {original_totals['draw']:.2f}, {original_totals['away_win']:.2f}")

    total_matches = qs.count()
    qs = qs.annotate(
        combined_score=Concat(
            Cast('home_score', output_field=CharField()),
            Value('-'),
            Cast('away_score', output_field=CharField()),
            output_field=CharField()
        ),

    ).values('combined_score', 'home_score', 'away_score').annotate(
        count=Count('combined_score')
    ).order_by('combined_score', 'home_score', 'away_score')

    prob_home_win, prob_draw, prob_away_win = 0, 0, 0

    # Calculate adjustment factors
    adjustment_factors = {
        'home_win': home_win / original_totals['home_win'],
        'draw': draw / original_totals['draw'],
        'away_win': away_win / original_totals['away_win'],
    }

    # Calculate joint probabilities for all match outcomes
    for row in qs:
        match_prob = row['count'] / total_matches
        i = row['home_score']
        j = row['away_score']
        # Check the match outcome
        if i > j:
            match_prob *= adjustment_factors['home_win']
            prob_home_win += match_prob
        elif i < j:
            match_prob *= adjustment_factors['away_win']
            prob_away_win += match_prob
        else:
            match_prob *= adjustment_factors['draw']
            prob_draw += match_prob
        score = row['combined_score']
        # logging.info(f"Probability of {score} score: {match_prob:.5f} odds: {1/match_prob:.3f}")
        MonivetoProb.objects.update_or_create(
            combination=f"{match_nro}-{score}",
            moniveto_id=moniveto_id,
            list_index=list_index,
            defaults={
                "match_nro": match_nro,
                "score": f"{score}",
                "prob": match_prob#*0.95,
            }
        )

    print(f"Probabilities {prob_home_win:.2f} {prob_draw:.2f} {prob_away_win:.2f}")
