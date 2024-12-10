<!--A terminal assistant for the hopelessly confused-->

# wut

**CLI that summarizes the output of the previous console command.**

Just type in `wut` and an LLM of your choice will explain what's in your terminal. You can use it to:

- Understand and debug stack traces
- Decipher error codes
- Fix incorrect commands
- Summarize logs

![Demo](./demo.gif)

## Installation

```bash
> pipx install wut-cli
```

<!-- On MacOS or Linux, you can install via Homebrew:

```bash
> brew install wut
```

On other systems, you can install using pip:

```bash
> pipx install wut-cli
``` -->

Once installed, you can choose either OpenAI or Claude as your LLM provider. Just ensure you have the appropriate key added to your environment:

```bash
> export OPENAI_API_KEY="..."
> export ANTHROPIC_API_KEY="..."
```

## Usage

`wut` must be used inside a tmux or screen session. To use it, just type `wut` after running a command:

```bash
> git create-pr
git: 'create-pr' is not a git command.
> wut
```

You'll quickly get a brief explanation of the issue:

```markdown
This error occurs because `create-pr` is not a standard Git command. Git doesn't have a built-in `create-pr` command. To create a pull request, you typically need to:

1. Push your branch to the remote repository
2. Use the web interface of GitHub
```

If you have a _specific question_ about your last command, you can include a query:

```bash
> brew install pip
...
> wut "how do i add this to my PATH variable?"
```

## Roadmap

1. [If possible,](https://stackoverflow.com/questions/24283097/reusing-output-from-last-command-in-bash/75629157#75629157) capture terminal output _outside_ a tmux or screen session.
2. Add a `--fix` option to automatically execute a command suggested by `wut`.
