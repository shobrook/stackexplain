# Standard library
import sys
import os

import openai

# Local
import stackexplain.utilities.chatgpt as gpt
import stackexplain.utilities.printers as printers
import stackexplain.utilities.code_execution as code_exec


######
# MAIN
######

def handle_exit():
    """
    Handles ctrl-c nicely.
    """
    print()
    exit(0)


def main():
    try:
        args = sys.argv
        if len(args) == 1 or args[1].lower() in ("-h", "--help"):
            printers.print_help_message()
            return

        if not os.getenv("OPENAI_API_KEY"):
            printers.print_api_key_missing_message()
            return

        error_message = code_exec.execute_code(args[1::])
        if not error_message:
            return

        print()

        explanation_stream = None
        error = None

        with printers.LoadingMessage():
            try:
                explanation_stream = gpt.get_chatgpt_explanation(error_message)
            except openai.error.OpenAIError as err:
                error = err

        if not explanation_stream:
            printers.print_openai_api_error(error)
            exit(3)

        printers.stream_error_explanation(explanation_stream)
    except KeyboardInterrupt:
        handle_exit()
