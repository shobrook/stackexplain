from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep

# ASCII color codes
GREEN = '\033[92m'
GRAY = '\033[90m'
CYAN = '\033[36m'
RED = '\033[31m'
YELLOW = '\033[33m'
END = '\033[0m'
UNDERLINE = '\033[4m'
BOLD = '\033[1m'


######
# MAIN
######


def register_openai_credentials():
    pass # TODO


def print_help_message():
    pass # TODO


def print_invalid_language_message():
    # TODO: Colorize this better
    print(f"\n{RED}Sorry, stackexplain doesn't support this file type.\n{END}")


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
        self.message = "Asking ChatGPT to explain your error"
        # self.end = ""
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns

        print("\r" + " " * cols, end="", flush=True)
        # print(f"\r{self.end}", flush=True)

    def _animate(self):
        for step in cycle(self.steps):
            if self.done:
                break

            print(f"\r{step} {self.message}", flush=True, end="")

            sleep(self.timeout)

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()
