from revChatGPT.revChatGPT import Chatbot

# TEMP: Have user fill this out
config = {}


#########
# HELPERS
#########


def construct_query(language, error_message):
    language = "java" if language == "javac" else language
    language = "python" if language == "python3" else language
    language = "go" if language == "go run" else language

    # TODO: Create an enum for mapping languages to exec commands
    query = f"Explain this {language} error message in brief and simple terms:"
    query += "\n```"
    query += f"\n{error_message}"
    query += "\n```"

    return query


######
# MAIN
######


def is_user_registered():
    return True # TODO


def register_openai_credentials():
    pass # TODO


def get_chatgpt_explanation(language, error_message):
    query = construct_query(language, error_message)
    chatbot = Chatbot(config, conversation_id=None)
    return chatbot.get_chat_response(query)["message"].strip()
