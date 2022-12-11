# Standard library
import json
import os.path as path

# Third party
from revChatGPT.revChatGPT import Chatbot

# to manage the passwd, also third party
from cryptography.fernet import Fernet
from getpass import getpass

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

    email = str(input("Insert your email: "))      

    # Get Password & Encrypt
    master_secret_key = getpass()
    print()
    key = Fernet.generate_key()
    key = key.decode('utf-8')
    config = {"email": email, "password": key}
    open(CONFIG_FP, 'w').close() # blanks the file
    with open(CONFIG_FP, "w") as config_file:
        json.dump(config, config_file)


def get_chatgpt_explanation(language, error_message):
    password_prompt = getpass("\n\nPASSWORD (if you don't press ENTER the program won't load): \n\n")
    password = password_prompt.encode('utf-8')
    key = None
    email = None
    with open(CONFIG_FP, "r") as file:
        try:
            read = json.load(file)
        except:
            print(CONFIG_FP, "\t doesn't exist")
            return
        email = read["email"]
        key = read["password"]
    cipher = Fernet(key)
    token = cipher.encrypt(password)
    password = cipher.decrypt(token).decode('utf-8')
    config = {"email": email, "password": password}
    query = construct_query(language, error_message)
    chatbot = Chatbot(config)
    return chatbot.get_chat_response(query)["message"].strip()
