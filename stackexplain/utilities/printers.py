# Standard library
import sys
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep
from random import random

# Third party
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import Terminal256Formatter

CODE_IDENTIFIER = "```"
CODE_INDENT = "    "

# ASCII color codes
GREEN = "\033[92m"
GRAY = "\033[90m"
CYAN = "\033[36m"
RED = "\033[31m"
YELLOW = "\033[33m"
END = "\033[0m"
UNDERLINE = "\033[4m"
BOLD = "\033[1m"


#########
# HELPERS
#########


def slow_print(text, delay=0.01):
    for word in text:
        sys.stdout.write(word)
        sys.stdout.flush() # Defeat buffering

        sleep(delay)


######
# MAIN
######


def print_help_message():
    pass # TODO


def print_invalid_language_message():
    # TODO: Colorize this better
    print(f"\n{RED}Sorry, stackexplain doesn't support this file type.\n{END}")


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

        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
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
            # TODO: Handle bolds
            slow_print(text)

            continue

        code = highlight(
            text,
            lexer=get_lexer_by_name("python"),
            formatter=Terminal256Formatter(style="solarized-dark")
        )
        for line in code.strip().split("\n"):
            slow_print(f"{CODE_INDENT}{line}", delay=0.001)
            print()

    print("\n")
