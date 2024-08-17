import os

# Retrieve the API key from the environment variable
api_key = os.getenv('OPENAI_API_KEY')

# Print the API key to check its value
print(f'OPENAI_API_KEY: {api_key}')

# Use the API key with OpenAI or any other service
# openai.api_key = api_key