import sys

import utilities.chatgpt as gpt
import utilities.parsers as parsers
import utilities.printers as printers
import utilities.code_execution as code_exec


def main():
    # TODO: Check if local config file is populated
    # If not, prompt user to enter OpenAI credentials

    args = sys.argv
    if len(args) == 1 or args[1].lower() in ("-h", "--help"):
        printers.print_help_message()
        return

    language = parsers.get_language(args)
    if not language:
        printers.print_invalid_language_message()
        return

    if not gpt.is_user_registered():
        gpt.register_openai_credentials()

    error_message = code_exec.execute_code(args, language)
    if not error_message:
        return

    print()

    with printers.LoadingMessage(): # Context-based loading message
        explanation = gpt.get_chatgpt_explanation(language, error_message)

    # TODO: Add syntax highlighting to code

    printers.print_error_explanation(explanation)
