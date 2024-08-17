import requests
import os
import config 

# Retrieve the API key from environment variables
api_key = os.getenv('API_KEY_1')
api_key = config.API_KEY_1

# Define the headers for authentication
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Define the messages for the chat
messages = [
    {
        "role": "system",
        "content": (
            "You are an artificial intelligence assistant and you need to "
            "engage in a helpful, detailed, polite conversation with a user. Response limit to 20 words only."
        ),
    },
    {
        "role": "user",
        "content": "How many gold india won in olympic 2024",
    },
]

# Define the API endpoint for chat completion
url = "https://api.perplexity.ai/chat/completions"

# Make a POST request to the Perplexity API for chat completion
response = requests.post(url, headers=headers, json={"model": "llama-3.1-sonar-huge-128k-online", "messages": messages})

# Print the response content
if response.status_code == 200:
    print(response.json()['choices'][0]['message']['content'])
else:
    print(f"Error: {response.status_code} - {response.text}")

