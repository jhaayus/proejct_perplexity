import requests
from openai import OpenAI

import os


api_key = os.getenv('API_KEY_1')
api_key = api_key
api_url = 'https://api.perplexity.ai'  # Replace with the actual endpoint

def ask_question(question):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'question': question
    }
    
    response = requests.post(api_url, headers=headers, json=data)
    
    if response.status_code == 200:
        answer = response.json().get('answer')
        return answer
    else:
        return f"Error: {response.status_code} - {response.text}"

# Example usage
question = "What is the capital of France?"
answer = ask_question(question)
print(f"Question: {question}\nAnswer: {answer}")