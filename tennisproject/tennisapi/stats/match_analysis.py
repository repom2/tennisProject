from django.conf import settings
import logging
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from django.conf import settings


def match_analysis(
    player_name,
    opponent_name,
    player_info,
    md_table,
    event_spw,
    event_rpw,
    tour_spw,
    tour_rpw,
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
                Here is tennis player {player_name} latest tennis matches and statistics. 
                The next opponent is {opponent_name}.
                Player info: {player_info}.
                Last matches: {md_table}.
                
            What you can tell about player's path to this match. How difficult matches
            she is faced recently when you look at for example the opponents ranking 
            (vRank). Is there something noticeable in the stats. Is there retirements
            or walkovers in the matches. Have the player been long time out of the game.
            Is the player stayed long time on court in this tournament or nearby 
            tournaments. Date in the matches is tournament start date so next round 
            match is played after this date. 1stin is the first serve in percentage.
            1st% is the first serve won percentage. 2nd% is the second serve won
            percentage. A% ace percentage. DF% double fault percentage. BPSvd% break point
            saved percentage. RP% return point won percentage. Rd is the round in the
            tournament.
            
            Court Speed:
            Current tournament service points won {event_spw} and return point won
            percentage {event_rpw}.
            Tour average service points won {tour_spw} and return point won percentage
            {tour_rpw}.
        """
    )

    messages = [system_msg, user_msg]
    ai_message = chatgpt(messages)

    # Full preview
    preview = ai_message.content
    print("Full preview")
    print(ai_message.content)
    messages.append(ai_message)

    user_msg = HumanMessage(content=f"""Explain this shortly better constructed way.""")
    messages.append(user_msg)
    ai_message = chatgpt(messages)

    # Short preview
    reasoning = ai_message.content
    print("Short preview")
    print(reasoning)

    return preview, reasoning


# if __name__ == '__main__':
#   print(OPENAI_API_KEY)
