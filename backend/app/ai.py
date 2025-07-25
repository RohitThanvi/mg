import requests
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_ai_response(prompt: str) -> str:
    print(f"Getting AI response for prompt: {prompt}")
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

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)

    if response.status_code == 200:
        print("AI response received successfully.")
        return response.json()['choices'][0]['message']['content']
    else:
        print(f"AI failed to respond with status code: {response.status_code}")
        print(f"Response: {response.text}")
        return "AI failed to respond."
