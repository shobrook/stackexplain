mod context;
mod llm;
mod shell;

use clap::Parser;
use context::get_terminal_context;
use indicatif::{ProgressBar, ProgressStyle};
use llm::{explain, print_response};
use shell::get_shell;
use std::env;
use std::time::Duration;

/// CLI that explains the output of your last command
#[derive(Parser, Debug)]
#[command(name = "wut", version = "1.0")]
struct Args {
    /// A specific question about what's on your terminal.
    #[arg(long, default_value = "")]
    query: String,

    /// Print debug information.
    #[arg(long)]
    debug: bool,
}

fn main() {
    let args = Args::parse();
    let debug_print = |text: &str| {
        if args.debug {
            println!("wut | {}", text);
        }
    };

    // Initialize loading indicator
    let loader = ProgressBar::new_spinner();
    loader.enable_steady_tick(Duration::from_millis(80));
    loader.set_style(
        ProgressStyle::with_template("{spinner:.green.bold} {msg:.green.bold}")
            .unwrap()
            .tick_strings(&["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]),
    );
    loader.set_message("Figuring it out...");

    // Ensure environment is set up correctly
    if env::var("TMUX").is_err() && env::var("STY").is_err() {
        // TODO: Make this red
        println!("wut must be run inside a tmux or screen session.")
    }
    if env::var("OPENAI_API_KEY").is_err() && env::var("ANTHROPIC_API_KEY").is_err() {
        // TODO: Make this red
        println!("Please create an environment variable for your OpenAI or Anthropic API key.");
    }

    let shell = get_shell();
    let terminal_context = get_terminal_context(&shell);

    debug_print(&format!(
        "Retrieved shell information:\n- Name: {:?}\n- Path: {}\n- Prompt: {}",
        shell.name,
        shell.path.unwrap_or("Unknown".to_string()),
        shell.prompt.unwrap_or("Unknown".to_string())
    ));
    debug_print(&format!(
        "Retrieved terminal context:\n{}",
        terminal_context
    ));

    let response = explain(&terminal_context, Some(args.query.as_str()));
    loader.finish_and_clear();
    print_response(&response);
}
