from django.conf import settings
import logging
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from django.conf import settings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)


def match_analysis(player_name, opponent_name, player_info, md_table):
    open_api_key = settings.OPENAI_API_KEY

    chatgpt = ChatOpenAI(
        openai_api_key=open_api_key,
        model_name='gpt-4',
        temperature=0,
    )

    system_msg = SystemMessage(
        content="""
                    Your are a sport journalist. You are writing an short preview about tennis match.
                """
    )
    user_msg = HumanMessage(
        content=f"""
                Here is tennis player {player_name} latest tennis matches and statistics. 
                The next opponent is {opponent_name}.
                Player info: {player_info}.
                Last matches: {md_table}.
                
            What you can tell about {player_name} path to this match. How difficult matches she is faced when you look at the vRank 
            (opponents ranking). Is there something noticeable in the stats. Is there retirements or walkovers in the matches.
            Have {player_name} been long time out of the game or stayed long time on court in this tournament or even different countries.
            Date in the matches is tournament start date so next match is played after this date.
                """
    )

    messages = [system_msg, user_msg]
    ai_message = chatgpt(messages)
    
    # Full preview
    preview = ai_message.content
    #logging.info(ai_message.content)
    messages.append(ai_message)

    user_msg = HumanMessage(
        content=f"""Explain this shortly better constructed way."""
    )
    messages.append(user_msg)
    ai_message = chatgpt(messages)
    
    # Short preview
    reasoning = ai_message.content
    print(ai_message.content)

    return preview, reasoning


#if __name__ == '__main__':
 #   print(OPENAI_API_KEY)

