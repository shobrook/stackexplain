# Standard library
import os
import tempfile
from collections import namedtuple
from subprocess import check_output, run, CalledProcessError
from typing import List, Optional, Tuple

# Third party
from ollama import chat
from psutil import Process
from openai import OpenAI
from anthropic import Anthropic
from google import genai
from google.genai import types
from rich.markdown import Markdown
import subprocess

from wut.prompts import EXPLAIN_PROMPT, ANSWER_PROMPT

# from prompts import EXPLAIN_PROMPT, ANSWER_PROMPT

MAX_CHARS = 10000
MAX_COMMANDS = 3
SHELLS = ["bash", "fish", "zsh", "csh", "tcsh", "powershell", "pwsh"]

Shell = namedtuple("Shell", ["path", "name", "prompt"])
Command = namedtuple("Command", ["text", "output"])


#########
# HELPERS
#########


def count_chars(text: str) -> int:
    return len(text)


def truncate_chars(text: str, reverse: bool = False) -> str:
    return text[-MAX_CHARS:] if reverse else text[:MAX_CHARS]


def get_shell_name(shell_path: Optional[str] = None) -> Optional[str]:
    if not shell_path:
        return None

    if os.path.splitext(shell_path)[-1].lower() in SHELLS:
        return os.path.splitext(shell_path)[-1].lower()

    if os.path.splitext(shell_path)[0].lower() in SHELLS:
        return os.path.splitext(shell_path)[0].lower()

    if shell_path.lower() in SHELLS:
        return shell_path.lower()

    return None


def get_shell_name_and_path() -> Tuple[Optional[str], Optional[str]]:
    path = os.environ.get("SHELL", None) or os.environ.get("TF_SHELL", None)
    if shell_name := get_shell_name(path):
        return shell_name, path

    proc = Process(os.getpid())
    while proc is not None and proc.pid > 0:
        try:
            _path = proc.name()
        except TypeError:
            _path = proc.name

        if shell_name := get_shell_name(_path):
            return shell_name, _path

        try:
            proc = proc.parent()
        except TypeError:
            proc = proc.parent

    return None, path


def get_shell_prompt(shell_name: str, shell_path: str) -> Optional[str]:
    shell_prompt = None
    try:
        if shell_name == "zsh":
            cmd = [
                shell_path,
                "-i",  # Add interactive mode
                "-c",
                "print -P $PS1",
            ]
            shell_prompt = check_output(cmd, stderr=subprocess.PIPE, text=True)
        elif shell_name == "bash":
            # Uses parameter transformation; only supported in Bash 4.4+
            cmd = [
                shell_path,
                "echo",
                '"${PS1@P}"',
            ]
            shell_prompt = check_output(cmd, text=True)
        elif shell_name == "fish":
            cmd = [shell_path, "fish_prompt"]
            shell_prompt = check_output(cmd, text=True)
        elif shell_name in ["csh", "tcsh"]:
            cmd = [shell_path, "-c", "echo $prompt"]
            shell_prompt = check_output(cmd, text=True)
        elif shell_name in ["pwsh", "powershell"]:
            cmd = [shell_path, "-c", "Write-Host $prompt"]
            shell_prompt = check_output(cmd, text=True)
    except Exception as e:
        print(f"DEBUG: Shell prompt error: {str(e)}")  # Debug line
        pass

    return shell_prompt.strip() if shell_prompt else None


def get_pane_output() -> str:
    output_file = None
    output = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            output_file = temp_file.name

            if os.getenv("TMUX"):  # tmux session
                cmd = [
                    "tmux",
                    "capture-pane",
                    "-p",
                    "-S",
                    # f"-{MAX_HISTORY_LINES}",
                    "-",
                ]
                with open(output_file, "w") as f:
                    run(cmd, stdout=f, text=True)
            elif os.getenv("STY"):  # screen session
                cmd = ["screen", "-X", "hardcopy", "-h", output_file]
                check_output(cmd, text=True)
            else:
                return ""

            with open(output_file, "r") as f:
                output = f.read()
    except CalledProcessError as e:
        pass

    if output_file:
        os.remove(output_file)

    return output


def get_commands(pane_output: str, shell: Shell) -> List[Command]:
    commands = []
    buffer = []
    
    # Common prompt endings for various shells including p10k
    PROMPT_MARKERS = ['%', '$', '#', '❯', '>', '➜']
    
    for line in reversed(pane_output.splitlines()):
        if not line.strip():
            continue
        
        # Skip lines containing 'wut' command
        if 'wut' in line:
            continue
            
        # Try exact prompt match first
        if shell.prompt and shell.prompt.lower() in line.lower():
            command_text = line.split(shell.prompt, 1)[1].strip()
            if command_text:  # Only if we found a non-empty command
                command = Command(command_text, "\n".join(reversed(buffer)).strip())
                commands.append(command)
                buffer = []
            continue
            
        # Fall back to checking for common prompt endings
        found_command = False
        for marker in PROMPT_MARKERS:
            # Only split on markers at the start of the line (allowing for whitespace)
            if line.lstrip().startswith(marker):
                try:
                    command_text = line.lstrip().split(marker, 1)[1].strip()
                    if command_text:  # Only if we found a non-empty command
                        command = Command(command_text, "\n".join(reversed(buffer)).strip())
                        commands.append(command)
                        buffer = []
                        found_command = True
                        break
                except IndexError:
                    continue
                    
        if found_command:  # If we found a command, move to next line
            continue
            
        buffer.append(line)
    
    return commands  # No need to exclude first command since we're filtering 'wut'


def truncate_commands(commands: List[Command]) -> List[Command]:
    num_chars = 0
    truncated_commands = []
    for command in commands:
        command_chars = count_chars(command.text)
        if command_chars + num_chars > MAX_CHARS:
            break
        num_chars += command_chars

        output = []
        for line in reversed(command.output.splitlines()):
            line_chars = count_chars(line)
            if line_chars + num_chars > MAX_CHARS:
                break

            output.append(line)
            num_chars += line_chars

        output = "\n".join(reversed(output))
        command = Command(command.text, output)
        truncated_commands.append(command)

    return truncated_commands


def truncate_pane_output(output: str) -> str:
    hit_non_empty_line = False
    lines = []  # Order: newest to oldest
    for line in reversed(output.splitlines()):
        if line and line.strip():
            hit_non_empty_line = True

        if hit_non_empty_line:
            lines.append(line)

    lines = lines[1:]  # Remove wut command
    output = "\n".join(reversed(lines))
    output = truncate_chars(output, reverse=True)
    output = output.strip()

    return output


def command_to_string(command: Command, shell_prompt: Optional[str] = None) -> str:
    shell_prompt = shell_prompt if shell_prompt else "$"
    command_str = f"{shell_prompt} {command.text}"
    command_str += f"\n{command.output}" if command.output.strip() else ""
    return command_str


def format_output(output: str) -> str:
    return Markdown(
        output,
        code_theme="monokai",
        inline_code_lexer="python",
        inline_code_theme="monokai",
    )


def run_anthropic(system_message: str, user_message: str) -> str:
    anthropic = Anthropic()
    response = anthropic.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=system_message,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def run_openai(system_message: str, user_message: str) -> str:
    openai = OpenAI(base_url=os.getenv("OPENAI_BASE_URL", None))
    response = openai.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        model=os.getenv("OPENAI_MODEL", None) or "gpt-4o",
        temperature=0.7,
    )
    return response.choices[0].message.content

def run_google(system_message: str, user_message: str) -> str:
    client = genai.Client()
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", None) or 'gemini-2.0-flash-exp',
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_message,
            temperature=0.7,
            max_output_tokens=4096
        ),
    )
    return response.text

def run_ollama(system_message: str, user_message: str) -> str:
    response = chat(
        model=os.getenv("OLLAMA_MODEL", None),
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
    )
    return response.message.content


def get_llm_provider() -> str:
    if os.getenv("OPENAI_API_KEY", None):  # Default
        return "openai"

    if os.getenv("ANTHROPIC_API_KEY", None):
        return "anthropic"

    if os.getenv("OLLAMA_MODEL", None):
        return "ollama"
    
    if os.getenv("GOOGLE_API_KEY", None):
        return "google"

    raise ValueError("No API key found for OpenAI, Anthropic, or Google.")


######
# MAIN
######


def get_shell() -> Shell:
    name, path = get_shell_name_and_path()
    prompt = get_shell_prompt(name, path)
    return Shell(path, name, prompt)  # NOTE: Could all be null values


def get_terminal_context(shell: Shell) -> str:
    pane_output = get_pane_output()
    if not pane_output:
        return "<terminal_history>No terminal output found.</terminal_history>"

    if not shell.prompt:
        # W/o the prompt, we can't reliably separate commands in terminal output
        pane_output = truncate_pane_output(pane_output)
        context = f"<terminal_history>\n{pane_output}\n</terminal_history>"
    else:
        commands = get_commands(pane_output, shell)
        commands = truncate_commands(commands[:MAX_COMMANDS])
        commands = list(reversed(commands))  # Order: Oldest to newest
        
        # Add check for empty commands list
        if not commands:
            return "<terminal_history>No commands found in terminal output.</terminal_history>"

        previous_commands = commands[:-1]
        last_command = commands[-1]

        context = "<terminal_history>\n"
        context += "<previous_commands>\n"
        context += "\n".join(
            command_to_string(c, shell.prompt) for c in previous_commands
        )
        context += "\n</previous_commands>\n"
        context += "\n<last_command>\n"
        context += command_to_string(last_command, shell.prompt)
        context += "\n</last_command>"
        context += "\n</terminal_history>"

    return context


def build_query(context: str, query: Optional[str] = None) -> str:
    if not (query and query.strip()):
        query = "Explain the last command's output. Use the previous commands as context, if relevant, but focus on the last command."

    return f"{context}\n\n{query}"


def explain(context: str, query: Optional[str] = None) -> str:
    system_message = EXPLAIN_PROMPT if not query else ANSWER_PROMPT
    user_message = build_query(context, query)
    provider = get_llm_provider()

    call_llm = run_openai
    if provider == "anthropic":
        call_llm = run_anthropic
    elif provider == "google":
        call_llm = run_google
    elif provider == "ollama":
        call_llm = run_ollama

    output = call_llm(system_message, user_message)
    return format_output(output)
