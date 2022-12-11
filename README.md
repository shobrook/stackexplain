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
$ stackexplain [file_path]
```

```bash
$ stackexplain -credentials
```

This will execute the file and, if an error is thrown, send the stack trace to ChatGPT and display its explanation in your terminal.

Note that when you first use `stackexplain`, you'll be asked to enter your OpenAI credentials.

__Supported file types:__ Python, Node.js, Ruby, Golang, and Java.
