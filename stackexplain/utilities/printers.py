# Standard library
import sys
import re
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep

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


######
# MAIN
######


def print_help_message():
    """
    Prints usage instructions.
    """

    print(f"{BOLD}StackExplain – Made by @shobrook{END}")
    print("Command-line tool that automatically explains your error messages using ChatGPT.")
    print(f"\n\n{UNDERLINE}Usage:{END} $ stackexplain [-h] {CYAN}<command_line_argument> [<additional_arguments>...]{END}")
    print(f"\n$ python3 {CYAN}test.py{END}   =>   $ stackexplain {CYAN}python3 test.py{END}")


def print_api_key_missing_message():
    print(f"\n{RED}Could not find OPENAI_API_KEY, please add this as an environment variable to use stackexplain.\n{END}", file=sys.stderr)

def print_openai_api_error(err):
    print(f"\n{RED}{err}\n{END}", file=sys.stderr)

def stream_error_explanation(streamer):
    for chunk in streamer:
        delta = chunk["choices"][0]["delta"]

        try:
            content = delta["content"]

            sys.stdout.write(content)
            sys.stdout.flush()
        except:
            pass

    print()


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
