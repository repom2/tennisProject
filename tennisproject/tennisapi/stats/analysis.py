import logging
import os

from django.conf import settings
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage


def match_analysis(data):
    open_api_key = settings.OPENAI_API_KEY
    logging.info(f"OpenAI API key: {open_api_key}")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler("openai_analysis.log", "w", "utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    chatgpt = ChatOpenAI(
        openai_api_key=open_api_key,
        model_name="gpt-4",
        temperature=0,
    )

    system_msg = SystemMessage(
        content="""
                    Your are a sport journalist. You are writing an short preview about tennis match.
                """
    )
    user_msg = HumanMessage(
        content=f"""
                Match is played between {data['winner_first_name']} {data['winner_name']} and 
                {data['loser_first_name']} {data['loser_name']}. What can you say about these players? 
                Is there any interesting facts about them head 2 head matches?
                Is there weakneases in their game? What is their current form? What is their ranking? What is their best ranking? What is their best result in this tournament?
                
                Elo Rating probability of home player winning is {data['prob']}.
                Home player service points won is {data['spw1']} and away player service points won is {data['spw2']}.
                Home player return points won is {data['rpw1']} and away player service points won is {data['rpw2']}.
                Home player calculatd probability of winning calculated from service and return stats is {data['win']}.
                
                They have been played {data['c']} matches against each other and home player winning perventage is {data['h2h']}.
                When calculating winning percentage using common opponent algorithm the home player winning percentage is {data['win_c']} and they were found 60 common opponent 
                between these rivals.
                """
    )

    messages = [system_msg, user_msg]
    ai_message = chatgpt(messages)
    preview = ai_message.content
    logging.info(ai_message.content)
    messages.append(ai_message)

    user_msg = HumanMessage(
        content=f"""
                What would be the best bet on this match 
                when home player odds are {data['odds1']} 
                and away player odds are {data['odds2']}?
                If you take consider previous review and you
                need to find value bet, what would it be?
                If you take consider probability of winning and odds multiplier, 
                and value should be over 1, 
                of course you can pass the match if there is no value.
                """
    )
    messages.append(user_msg)
    ai_message = chatgpt(messages)
    reasoning = ai_message.content
    logging.info(ai_message.content)

    return preview, reasoning


# if __name__ == '__main__':
#   print(OPENAI_API_KEY)
