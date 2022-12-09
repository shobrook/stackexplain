# Standard library
import json
import os.path as path

# Third party
from revChatGPT.revChatGPT import Chatbot

# Local
from stackexplain.utilities.printers import prompt_user_for_credentials

CONFIG_FP = path.join(path.expanduser("~"), ".stackexplain.json")


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


def is_user_registered():
    return path.exists(CONFIG_FP)


def register_openai_credentials():
    email, password = prompt_user_for_credentials()
    config = {"email": email, "password": password}

    with open(CONFIG_FP, "w") as config_file:
        json.dump(config, config_file)


def get_chatgpt_explanation(language, error_message):
    config = json.load(open(CONFIG_FP))
    query = construct_query(language, error_message)
    chatbot = Chatbot(config)
    return chatbot.get_chat_response(query)["message"].strip()
