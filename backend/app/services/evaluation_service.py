from app.models import Message
from typing import List
from app.ai import get_ai_response

def evaluate_debate(messages: List[Message]):
    """
    Evaluates a debate and returns the winner.
    """
    # This is a placeholder for a more sophisticated evaluation metric.
    # For now, we will just count the number of messages.
    user_messages = [m for m in messages if m.sender_type == 'user']
    opponent_messages = [m for m in messages if m.sender_type != 'user']

    if len(user_messages) > len(opponent_messages):
        return 'user'
    elif len(opponent_messages) > len(user_messages):
        return 'opponent'
    else:
        return 'draw'

def get_debate_analysis(messages: List[Message]):
    """
    Returns an analysis of a debate.
    """
    prompt = "The following is a transcript of a debate. Please provide an analysis of the debate, including the strengths and weaknesses of each debater's arguments.\n\n"
    for message in messages:
        prompt += f"{message.sender.username if message.sender else 'AI'}: {message.content}\n"

    analysis = get_ai_response(prompt)
    return analysis
