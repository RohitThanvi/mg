import requests
import os
import logging

logging.basicConfig(level=logging.INFO)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_ai_response(prompt: str) -> str:
    logging.info(f"Getting AI response for prompt: {prompt}")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are an expert debater."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
        response.raise_for_status()
        logging.info("AI response received successfully.")
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while calling the Groq API: {e}")
        return "AI failed to respond."
