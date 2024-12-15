use crate::shell::Shell;
use std::fs::File;
use std::io::Read;
use std::process::{Command, Stdio};
use tempfile::NamedTempFile;

const MAX_CHARS: usize = 10000;
const MAX_COMMANDS: usize = 3;

struct TerminalCommand {
    command: String,
    output: String,
}

/*
HELPERS
*/

fn command_to_string(command: &TerminalCommand, shell_prompt: Option<&str>) -> String {
    let shell_prompt = shell_prompt.unwrap_or("$");
    let mut command_str = format!("{} {}", shell_prompt, command.command);
    if !command.output.trim().is_empty() {
        command_str.push_str(&format!("\n{}", command.output));
    }
    command_str
}

fn count_chars(text: &str) -> usize {
    text.chars().count()
}

fn truncate_text(text: &str, reverse: bool) -> String {
    let chars: Vec<char> = text.chars().collect();
    let truncated_chars: Vec<char> = if reverse {
        chars.iter().rev().take(MAX_CHARS).rev().cloned().collect()
    } else {
        chars.iter().take(MAX_CHARS).cloned().collect()
    };
    truncated_chars.into_iter().collect()
}

fn get_terminal_history() -> Option<String> {
    let mut output_file = None;
    let mut output = String::new();

    if let Ok(temp_file) = NamedTempFile::new() {
        output_file = Some(temp_file.path().to_path_buf());

        let cmd_result = if std::env::var("TMUX").is_ok() {
            // tmux session
            Command::new("tmux")
                .arg("capture-pane")
                .arg("-p")
                .arg("-S")
                .arg("-")
                .stdout(Stdio::from(temp_file.reopen().unwrap()))
                .status()
        } else if std::env::var("STY").is_ok() {
            // screen session
            Command::new("screen")
                .arg("-X")
                .arg("hardcopy")
                .arg("-h")
                .arg(temp_file.path())
                .status()
        } else {
            return None;
        };

        if cmd_result.is_ok() {
            if let Ok(mut file) = File::open(temp_file.path()) {
                file.read_to_string(&mut output).ok();
            }
        }
    }

    if let Some(output_file) = output_file {
        std::fs::remove_file(output_file).ok();
    }

    Some(output)
}

fn get_commands(history: &str, shell: &Shell) -> Vec<TerminalCommand> {
    /*
    TODO: Handle edge cases. E.g. if you change the shell prompt in the middle of a session,
    only the latest prompt will be used to split the pane output into `TerminalCommand` objects.
    Or if the shell prompt has ASCII escape codes in it (e.g. for colors), we must
    remove them before splitting the history.
    */

    let mut commands = Vec::new(); // Order: newest to oldest
    let mut buffer = Vec::new();

    for line in history.lines().rev() {
        if line.trim().is_empty() {
            continue;
        }

        if let Some(prompt) = &shell.prompt {
            if line.to_lowercase().contains(&prompt.to_lowercase()) {
                if let Some((_, command_text)) = line.split_once(prompt) {
                    let command_text = command_text.trim();
                    let command_output = buffer
                        .iter()
                        .rev()
                        .cloned()
                        .collect::<Vec<_>>()
                        .join("\n")
                        .trim()
                        .to_string();
                    commands.push(TerminalCommand {
                        command: command_text.to_string(),
                        output: command_output,
                    });
                    buffer.clear();
                }
                continue;
            }
        }

        buffer.push(line.to_string());
    }

    commands.into_iter().skip(1).collect() // Exclude the wut command itself
}

fn truncate_commands(commands: Vec<TerminalCommand>) -> Vec<TerminalCommand> {
    let mut num_chars = 0;
    let mut truncated_commands = Vec::new();

    for command in commands {
        let command_chars = count_chars(&command.command);
        if command_chars + num_chars > MAX_CHARS {
            break;
        }
        num_chars += command_chars;

        let mut output = Vec::new();
        for line in command.output.lines().rev() {
            let line_chars = count_chars(line);
            if line_chars + num_chars > MAX_CHARS {
                break;
            }

            output.push(line.to_string());
            num_chars += line_chars;
        }

        output.reverse();
        let output = output.join("\n");
        let truncated_command = TerminalCommand {
            command: command.command.clone(),
            output,
        };
        truncated_commands.push(truncated_command);
    }

    truncated_commands
}

fn truncate_history(history: &str) -> String {
    let mut hit_non_empty_line = false;
    let mut lines: Vec<&str> = Vec::new(); // Order: newest to oldest

    for line in history.lines().rev() {
        if !line.trim().is_empty() {
            hit_non_empty_line = true;
        }

        if hit_non_empty_line {
            lines.push(line);
        }
    }

    if !lines.is_empty() {
        lines.drain(0..2); // Remove wut command
    }

    let history = lines.into_iter().rev().collect::<Vec<&str>>().join("\n");
    let history = truncate_text(&history, true);
    history.trim().to_string()
}

/*
MAIN
*/

pub fn get_terminal_context(shell: &Shell) -> String {
    let history = get_terminal_history();
    if history.is_none() {
        return "<terminal_history>No terminal output found.</terminal_history>".to_string();
    }

    let history = history.unwrap();

    if shell.prompt.is_none() {
        // W/o the prompt, we can't reliably separate commands in terminal output
        let history = truncate_history(&history);
        return format!("<terminal_history>\n{}\n</terminal_history>", history);
    } else {
        let commands = get_commands(&history, shell);
        let commands = commands.into_iter().take(MAX_COMMANDS).collect::<Vec<_>>();
        let commands = truncate_commands(commands);
        let commands: Vec<TerminalCommand> = commands.into_iter().rev().collect(); // Order: Oldest to newest

        let previous_commands = &commands[..commands.len().saturating_sub(1)];
        let last_command: &TerminalCommand = commands.last().unwrap();

        let mut context = String::from("<terminal_history>\n");
        context.push_str("<previous_commands>\n");
        context.push_str(
            &previous_commands
                .iter()
                .map(|c: &TerminalCommand| command_to_string(c, shell.prompt.as_deref()))
                .collect::<Vec<String>>()
                .join("\n"),
        );
        context.push_str("\n</previous_commands>\n");
        context.push_str("\n<last_command>\n");
        context.push_str(&command_to_string(last_command, shell.prompt.as_deref()));
        context.push_str("\n</last_command>");
        context.push_str("\n</terminal_history>");

        return context;
    }
}
