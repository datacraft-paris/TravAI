import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")


with open('retrieval_output.json', 'r') as file:
    # Load the JSON data
    meal_analysis = json.load(file)

# Define the API endpoint
api_url = "https://api.mistral.ai/v1/chat/completions"

# Function to call the Mistral LLM
def call_mistral_llm_for_ingredient_matching(ingredient, propositions):
    # Prepare the input for the LLM
    prompt = (
        f"Given the ingredient '{ingredient}', match it with one of the following propositions "
        f"and return a dictionary with the ingredient name and the associated numeric value:\n"
        f"Propositions: {propositions}\n"
        "If the best match has a value of '-' instead of a numeric value, guess the value based on your general knowledge."
        "The output must be in format: {ingredient_name:numeric value}"
        "DO NOT generate any \ n token"
        "Only generate the json and no additionnal text"
        ""
    )

    # Prepare the request payload
    payload = {
        "model": "mistral-large-latest",
        "messages":  [{"role": "user", "content": prompt}],
        "temperature": 0,
        "response_format": {"type": "json_object"}
    }

    # Set the headers, including the API key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Make the API request
    response = requests.post(api_url, headers=headers, json=payload)

    # Check for a successful response
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]['content']
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

for ingredient, retrieved_values in meal_analysis.items():
    ingredient_with_kcal = call_mistral_llm_for_ingredient_matching(ingredient, retrieved_values)
    # Print or process the key and value
    print(ingredient_with_kcal)


