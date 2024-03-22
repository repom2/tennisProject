from django.conf import settings
import logging
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from django.conf import settings


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
                    which have to be considered when calculating match probabilities.
                """
    )
    user_msg = HumanMessage(
        content=f"""
                Here is tennis player {home_name} latest tennis matches and statistics. 
                The next opponent is {away_name}.
                Player info: {home_player_info}.
                Last matches: {home_table}.
                Calculated stats: {home_matches}.
                
                The opponent is {away_name}.
                Player info: {away_player_info}.
                Last matches: {away_table}.
                Calculated stats: {away_matches}.
                
                Elo rating based match probabilities: {elo_rating}.
            
            About the last matches data:
            What you can tell about player's path to this match. How difficult matches
            she is faced recently when you look at for example the opponents ranking 
            (vRank). Is there something noticeable in the stats. Is there retirements
            or walkovers in the matches. Winner is always left side in the match table if
             retirement or walkover is marked it is concerned the right side player. 
             Have the player been long time out of the game.
            Is the player stayed long time on court in this tournament or nearby 
            tournaments. Date in the matches is tournament start date. 
            1stin is the first serve in percentage.
            1st% is the first serve won percentage. 2nd% is the second serve won
            percentage. A% ace percentage. DF% double fault percentage. BPSvd% break point
            saved percentage. RP% return point won percentage. Rd is the round in the
            tournament. First match in match data is this match.
            
            From match data I have calculated stats for the players.
            And from these stats I have calculated probabilities for the match: 
            {stats_win} - {1 - stats_win}
            
            What I want to know when looking the match data, player info and elo rating
            that are the calculated stats comparable between the players.
            
            When looking elo rating or player rank and latest oppenent ranks is there
            big difference between players. Because calculated stats can be little bit off
            if other player opponents is much better than other player opponents.
            
            
        """
    )

    messages = [system_msg, user_msg]
    ai_message = chatgpt(messages)

    # Full preview
    preview = ai_message.content


    return preview


# if __name__ == '__main__':
#   print(OPENAI_API_KEY)
