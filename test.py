import openai
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Fetch the API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Specify the chat model
        messages=[
            {"role": "system", "content": "You are a creative marketing assistant."},
            {"role": "user", "content": "Suggest a creative slogan for a new organic coffee brand that emphasizes sustainability and fair trade."}
        ]
    )
    print("API Key is valid!")
    print("Generated Response:", response['choices'][0]['message']['content'])
except Exception as e:
    print("Error:", e)
