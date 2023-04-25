# StackExplain

Explain your error message in plain English using ChatGPT. Just run your file with the `stackexplain` command.

![Demo](demo.gif)

## Installation

You can install `stackexplain` with pip:

```bash
$ pip3 install stackexplain
```

## Usage

Running a file with `stackexplain` is just as easy as running it normally:

```bash
$ stackexplain <command_line_argument> [<additional_arguments>...]
```

This will execute the command and, if an error is thrown, send the stack trace to ChatGPT and display its explanation in your terminal.

Note: OpenAI API key is required in an environment variable called OPENAI_API_KEY
