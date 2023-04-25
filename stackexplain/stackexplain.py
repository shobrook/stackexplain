# Standard library
import sys
import os

# Local
import stackexplain.utilities.chatgpt as gpt
import stackexplain.utilities.parsers as parsers
import stackexplain.utilities.printers as printers
import stackexplain.utilities.code_execution as code_exec


######
# MAIN
######


def main():
    args = sys.argv
    if len(args) == 1 or args[1].lower() in ("-h", "--help"):
        printers.print_help_message()
        return

    language = parsers.get_language(args)
    if not language:
        printers.print_invalid_language_message()
        return

    if not os.getenv("OPENAI_API_KEY"):
        printers.print_api_key_missing_message()
        return

    error_message = code_exec.execute_code(args, language)
    if not error_message:
        return

    print()

    explanation_stream = None
    with printers.LoadingMessage():
        explanation_stream = gpt.get_chatgpt_explanation(language, error_message)

    printers.stream_error_explanation(explanation_stream)
