use reqwest::blocking::Client;
use serde_json::json;
use std::env;
use std::error::Error;
use termimad::MadSkin;

const EXPLAIN_PROMPT: &str = r#"<assistant>
You are a command-line assistant whose job is to explain the output of the most recently executed command in the terminal.
Your goal is to help users understand (and potentially fix) things like stack traces, error messages, logs, or any other confusing output from the terminal.
</assistant>

<instructions>
- Receive the last command in the terminal history and the previous commands before it as context.
- Explain the output of the last command.
- Use a clear, concise, and informative tone.
- If the output is an error or warning, e.g. a stack trace or incorrect command, identify the root cause and suggest a fix.
- Otherwise, if the output is something else, e.g. logs or a web response, summarize the key points.
</instructions>

<formatting>
- Use Markdown to format your response.
- Commands (both single and multi-line) should be placed in fenced markdown blocks.
- Code snippets should be placed in fenced markdown blocks.
- Only use bold for warnings or key takeaways.
- Break down your response into digestible parts.
- Keep your response as short as possible. No more than 5 sentences, unless the issue is complex.
</formatting>"#;

const ANSWER_PROMPT: &str = r#"<assistant>
You are a command-line assistant whose job is to answer the user's question about the most recently executed command in the terminal.
</assistant>

<instructions>
- Receive the last command in the terminal history and the previous commands before it as context.
- Use a clear, concise, and informative tone.
</instructions>

<formatting>
- Use Markdown to format your response.
- Commands (both single and multi-line) should be placed in fenced markdown blocks.
- Code snippets should be placed in fenced markdown blocks.
- Only use bold for warnings or key takeaways.
- Break down your response into digestible parts.
- Keep your response as short as possible. No more than 5 sentences, unless the issue is complex.
</formatting>"#;

#[derive(PartialEq)]
enum LLMProvider {
    OpenAI,
    Anthropic,
}

/*
HELPERS
*/

fn get_llm_provider() -> LLMProvider {
    if std::env::var("OPENAI_API_KEY").is_ok() {
        return LLMProvider::OpenAI;
    }

    if std::env::var("ANTHROPIC_API_KEY").is_ok() {
        return LLMProvider::Anthropic;
    }

    return LLMProvider::OpenAI;
}

fn run_openai(system_message: &str, user_message: &str) -> Result<String, Box<dyn Error>> {
    let api_key = env::var("OPENAI_API_KEY").expect("OPENAI_API_KEY not set");
    let client = Client::new();
    let request_body = json!({
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "temperature": 0.7
    });
    let response = client
        .post("https://api.openai.com/v1/chat/completions")
        .header("Content-Type", "application/json")
        .header("Authorization", format!("Bearer {}", api_key))
        .json(&request_body)
        .send()?;
    let response_json: serde_json::Value = response.json()?;
    let content = response_json["choices"][0]["message"]["content"]
        .as_str()
        .ok_or("Failed to extract content")?
        .to_string();

    Ok(content)
}

fn run_anthropic(system_message: &str, user_message: &str) -> Result<String, Box<dyn Error>> {
    let api_key = env::var("ANTHROPIC_API_KEY").expect("ANTHROPIC_API_KEY not set");
    let client = Client::new();
    let request_body = json!({
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1024,
        "system": system_message,
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ],
    });
    let response = client
        .post("https://api.anthropic.com/v1/messages")
        .header("Content-Type", "application/json")
        .header("x-api-key", api_key)
        .header("anthropic-version", "2023-06-01")
        .json(&request_body)
        .send()?;
    let response_json: serde_json::Value = response.json()?;
    let content = response_json["content"][0]["text"]
        .as_str()
        .ok_or("Failed to extract content")?
        .to_string();

    Ok(content)
}

fn build_query(context: &str, query: Option<&str>) -> String {
    let query = match query {
        Some(q) if !q.trim().is_empty() => q,
        _ => "Explain the last command's output. Use the previous commands as context, if relevant, but focus on the last command.",
    };

    format!("{}\n\n{}", context, query)
}

/*
MAIN
*/

pub fn explain(context: &str, query: Option<&str>) -> String {
    let system_message = if query.is_none() {
        EXPLAIN_PROMPT
    } else {
        ANSWER_PROMPT
    };
    let user_message = build_query(context, query);
    let provider = get_llm_provider();
    let output = if provider == LLMProvider::OpenAI {
        run_openai(&system_message, &user_message)
    } else {
        run_anthropic(&system_message, &user_message)
    };

    output.unwrap_or_else(|e| format!("Error: {}", e))
}

pub fn print_response(response: &str) {
    let mut skin = MadSkin::default();
    skin.set_headers_fg(termimad::crossterm::style::Color::Blue);
    skin.code_block
        .set_bg(termimad::crossterm::style::Color::DarkGrey);
    skin.print_text(&response);
}
