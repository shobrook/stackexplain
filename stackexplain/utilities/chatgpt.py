# Standard library
import os.path as path
import os
import sys

# Third party
import openai

#########
# HELPERS
#########


def construct_prompt(error_message):
    prompt = f"Explain this error message in brief and simple terms:"
    prompt += "\n```"
    prompt += f"\n{error_message}"
    prompt += "\n```"

    return prompt


######
# MAIN
######


def get_chatgpt_explanation(error_message):
    query = construct_prompt(error_message)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo") # if users have gpt-4 (or fine-tuned)

    response = openai.ChatCompletion.create(
        model=model,
        temperature=0.1,
        messages=[
            {
            "role": "user",
             "content": query,
             }
        ],
        stream=True,
    )

    return response
