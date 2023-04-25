# Standard library
import os.path as path
import os
import sys

# Third party
import openai

#########
# HELPERS
#########


def construct_query(language, error_message):
    # TODO: Create an class for mapping languages to exec commands
    language = "java" if language == "javac" else language
    language = "python" if language == "python3" else language
    language = "go" if language == "go run" else language

    query = f"Explain this {language} error message in brief and simple terms:"
    query += "\n```"
    query += f"\n{error_message}"
    query += "\n```"

    return query


######
# MAIN
######


def get_chatgpt_explanation(language, error_message):
    query = construct_query(language, error_message)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo") # if users have gpt-4 (or fine-tuned)

    response = openai.ChatCompletion.create(
        model=model,
        temperature=0,
        messages=[
            {
            "role": "user",
             "content": query,
             }
        ],
        stream=True,
    )

    return response
