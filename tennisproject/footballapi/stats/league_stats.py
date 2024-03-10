from django.db.models import Count, Case, When, Value, F, TextField
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)


def league_stats(league):
    qs = league.filter(
        home_score__isnull=False,
        away_score__isnull=False
    )

    predictions_qs = qs.annotate(
        outcome=Case(
            When(home_score__gt=F('away_score'), then=Value('home_win')),
            When(home_score=F('away_score'), then=Value('draw')),
            When(home_score__lt=F('away_score'), then=Value('away_win')),
            output_field=TextField()
        ))

    # Calculate original totals (this needs to be done in Python since Django ORM does not support dynamic aggregation based on annotated values)
    original_totals = {
        'home_win': predictions_qs.filter(
            outcome='home_win').count() / predictions_qs.count(),
        'draw': predictions_qs.filter(outcome='draw').count() / predictions_qs.count(),
        'away_win': predictions_qs.filter(
            outcome='away_win').count() / predictions_qs.count(),
    }
    logging.info(
        f"Total matches: {qs.count()}, Original totals: {original_totals['home_win']:.2f}, {original_totals['draw']:.2f}, {original_totals['away_win']:.2f}")
