# Standard library
import os
from queue import Queue
from subprocess import PIPE, Popen
from threading import Thread

# Local
from stackexplain.utilities.parsers import get_code_exec_command, get_error_message

GRAY = "\033[37m"
END = "\033[0m"


#########
# HELPERS
#########


def read(pipe, funcs):
    """
    Reads and pushes piped output to a shared queue and appropriate lists.
    """

    for line in iter(pipe.readline, b''):
        for func in funcs:
            func(line.decode("utf-8"))

    pipe.close()


def write(get):
    """
    Pulls output from shared queue and prints to terminal.
    """

    print()
    for line in iter(get, None):
        line = line.replace("\n", "")
        print(f"{GRAY}{line}{END}")


######
# MAIN
######


def execute_code(args, language):
    """
    Executes a given command in a subshell, pipes stdout/err to the current
    shell, and returns the stderr.
    """

    command = get_code_exec_command(args, language)
    process = Popen(
        command,
        cwd=None,
        shell=False,
        close_fds=True,
        stdout=PIPE,
        stderr=PIPE,
        bufsize=-1
    )

    output, errors = [], []
    pipe_queue = Queue()

    # Threads for reading stdout and stderr pipes and pushing to a shared queue
    stdout_thread = Thread(target=read, args=(process.stdout, [pipe_queue.put, output.append]))
    stderr_thread = Thread(target=read, args=(process.stderr, [pipe_queue.put, errors.append]))

    # Thread for printing items in the queue
    writer_thread = Thread(target=write, args=(pipe_queue.get,))

    # Spawns each thread
    for thread in (stdout_thread, stderr_thread, writer_thread):
        thread.daemon = True
        thread.start()

    process.wait()

    for thread in (stdout_thread, stderr_thread):
        thread.join()

    pipe_queue.put(None)

    # output = ''.join(output)
    errors = ''.join(errors)

    # File doesn't exist, for java, command[1] is a class name instead of a file
    if "java" != command[0] and not os.path.isfile(command[1]):
        return None

    return get_error_message(errors, language)
