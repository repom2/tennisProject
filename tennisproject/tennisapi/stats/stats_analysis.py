import logging
import os

from django.conf import settings
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage


def stats_analysis(
    home_name,
    away_name,
    home_player_info,
    away_player_info,
    home_table,
    away_table,
    stats_win,
    elo_rating,
    home_matches,
    away_matches,
):
    open_api_key = settings.OPENAI_API_KEY

    chatgpt = ChatOpenAI(openai_api_key=open_api_key, model_name="gpt-4", temperature=0)

    system_msg = SystemMessage(
        content="""
                    Your are a tennis analyst who pick most important aspect from stats
                    and consider is given calculated match probability correct.
                """
    )
    try:
        away_elo_rating = 1 - elo_rating
    except TypeError:
        away_elo_rating = None
    try:
        away_stats_win = 1 - stats_win
    except TypeError:
        away_stats_win = None
    user_msg = HumanMessage(
        content=f"""
                Tennis matchs is played between {home_name} and {away_name}.
                1. Player info: {home_player_info}.
                Latest match data: {home_table}.
                Calculated stats (winrate, service/return points won): {home_matches}.
                
                2. Player info: {away_player_info}.
                Latest match data: {away_table}.
                Calculated stats: {away_matches}.
                
                Elo rating based match probabilities: {elo_rating} / {away_elo_rating}.
            
            About the latest matches data:
            What you can tell about player's path to this match. How difficult matches
            she is faced recently when you look at for example the opponents ranking 
            (vRank). Lower rank means better player.
            Is there something noticeable in the stats. Is there retirements
            or walkovers in the matches. Winner is always left side in the match table if
             retirement or walkover is marked it is concerned the right side player. 
             Have the player been long time out of the game.
            Is the player stayed long time on court in this tournament or previous near
            tournament that can have impact. Date in the matches is tournament start date.
            1stin is the first serve in percentage.
            1st% is the first serve won percentage. 2nd% is the second serve won
            percentage. A% ace percentage. DF% double fault percentage. BPSvd% break point
            saved percentage. RP% return point won percentage. Rd is the round in the
            tournament. First match in match data is this match.
            
            From match data I have calculated stats for the players.
            And from these stats I have calculated probabilities for the match: 
            {home_name} {stats_win}% vs. {away_name} {away_stats_win}%
            
            What I want to know when looking the match data, player info and elo rating,
            that are the calculated stats comparable between the players. If not my calculation
            can be off.
            
            When looking elo rating or player rank and latest opponents ranks is there
            big difference between players. Because calculated stats can be little bit off
            if other player has faced much harder opponents.
        """
    )

    messages = [system_msg, user_msg]
    ai_message = chatgpt(messages)

    # Full preview
    preview = ai_message.content

    return preview


# if __name__ == '__main__':
#   print(OPENAI_API_KEY)
