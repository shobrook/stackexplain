# StackExplain

Automatically explain your error messages in plain English using ChatGPT. Just run your file with the `stackexplain` command.

![Demo](demo.gif)

## Installation

>Requires Python 3.0 or higher.

You can install StackExplain with pip:

`$ pip3 install stackexplain`

## Usage

Running a file with `stackexplain` is just as easy as running it normally:

`$ stackexplain [file_path]`

This will execute the file and, if an error is thrown, send the stack trace to ChatGPT and display its explanation in your terminal.

__Supported file types:__ Python, Node.js, Ruby, Golang, and Java.
