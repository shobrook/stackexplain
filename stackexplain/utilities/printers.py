# Standard library
import sys
import re
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep

# Third party
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import Terminal256Formatter

CODE_IDENTIFIER = "```"
CODE_INDENT = "    "

# ASCII color codes
CYAN = "\033[36m"
RED = "\033[31m"
END = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

INLINE_BY_STAR_IDENTIFIER = "\*(.*?)\*"
INLINE_BY_DASH_IDENTIFIER = "`(.*?)`"


#########
# HELPERS
#########


def handle_inline_code(text):
    replacer = lambda s: f"{BOLD}{s.group()}{END}"
    text = re.sub(INLINE_BY_STAR_IDENTIFIER, replacer, text)
    text = re.sub(INLINE_BY_DASH_IDENTIFIER, replacer, text)

    return text


def slow_print(text, delay=0.01):
    for word in text:
        sys.stdout.write(word)
        sys.stdout.flush() # Defeat buffering

        sleep(delay)


def slow_print_code(text, delay=0.0025):
    code = highlight(
        text,
        lexer=get_lexer_by_name("python"),
        formatter=Terminal256Formatter(style="gruvbox-dark")
    )
    for line in code.strip().split("\n"):
        slow_print(f"{CODE_INDENT}{line}", delay)
        print()


######
# MAIN
######


def print_help_message():
    """
    Prints usage instructions.
    """

    print(f"{BOLD}StackExplain – Made by @shobrook{END}")
    print("Command-line tool that automatically explains your error message using ChatGPT.")
    print(f"\n\n{UNDERLINE}Usage:{END} $ stackexplain {CYAN}[file_name]{END}")
    print(f"\n$ python3 {CYAN}test.py{END}   =>   $ stackexplain {CYAN}test.py{END}")


def print_invalid_language_message():
    print(f"\n{RED}Sorry, StackExplain doesn't support this file type.\n{END}")


def prompt_user_for_credentials():
    print(f"{BOLD}Please enter your OpenAI credentials.{END}\n")
    email = input("Email address: ")
    password = input("Password: ")

    return email, password


class LoadingMessage:
    def __init__(self, timeout=0.1):
        """
        A loader-like context manager

        Args:
            desc (str, optional): The loader's description. Defaults to "Loading...".
            end (str, optional): Final print. Defaults to "Done!".
            timeout (float, optional): Sleep time between prints. Defaults to 0.1.
        """

        # self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.steps = ['-', '/', '|', '\\']
        self.message = f"{BOLD}{CYAN}Asking ChatGPT to explain your error{END}"
        self.end = f"{BOLD}{CYAN}🤖 ChatGPT's Explanation:{END}"
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns

        print(f"\r{' ' * cols}", end="", flush=True)
        print(f"\r{self.end}\n", flush=True)

    def _animate(self):
        for step in cycle(self.steps):
            if self.done:
                break

            print(f"\r{CYAN}{step}{END} {self.message}", flush=True, end="")

            sleep(self.timeout)

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, tb):
        self.stop()


def print_error_explanation(explanation):
    for i, text in enumerate(explanation.split(CODE_IDENTIFIER)):
        if not i % 2:
            text = handle_inline_code(text)
            slow_print(text)

            continue

        slow_print_code(text)

    print("\n")
