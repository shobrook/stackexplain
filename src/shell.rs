use std::process::Command;
use sysinfo::System;

#[derive(Debug)]
pub enum ShellType {
    Bash,
    Fish,
    Zsh,
    Csh,
    Tcsh,
    Powershell,
    Pwsh,
}

impl ShellType {
    fn from_str(s: &str) -> Option<Self> {
        match s {
            "bash" => Some(ShellType::Bash),
            "fish" => Some(ShellType::Fish),
            "zsh" => Some(ShellType::Zsh),
            "csh" => Some(ShellType::Csh),
            "tcsh" => Some(ShellType::Tcsh),
            "powershell" => Some(ShellType::Powershell),
            "pwsh" => Some(ShellType::Pwsh),
            _ => None,
        }
    }
}

#[derive(Debug)]
pub struct Shell {
    pub path: Option<String>,
    pub name: Option<ShellType>,
    pub prompt: Option<String>,
}

/*
HELPERS
*/

fn get_shell_name(shell_path: Option<&str>) -> Option<ShellType> {
    if let Some(path) = shell_path {
        let lower_path: String = path.to_lowercase();

        let first_component = std::path::Path::new(&lower_path)
            .components()
            .next()
            .and_then(|c| c.as_os_str().to_str())
            .unwrap_or("");
        let last_component = std::path::Path::new(&lower_path)
            .file_stem()
            .and_then(|s| s.to_str())
            .unwrap_or("");

        if let Some(shell_type) = ShellType::from_str(last_component) {
            return Some(shell_type);
        }

        if let Some(shell_type) = ShellType::from_str(first_component) {
            return Some(shell_type);
        }

        if let Some(shell_type) = ShellType::from_str(&lower_path) {
            return Some(shell_type);
        }
    }
    None
}

fn get_shell_path() -> Option<String> {
    let path = std::env::var("SHELL")
        .ok()
        .or_else(|| std::env::var("TF_SHELL").ok());
    if let Some(ref p) = path {
        if get_shell_name(Some(p)).is_some() {
            return Some(p.clone());
        }
    }

    let mut sys = System::new_all();
    sys.refresh_all();

    if let Ok(current_pid) = sysinfo::get_current_pid() {
        let mut current_pid = current_pid;
        while current_pid.as_u32() > 0 {
            if let Some(process) = sys.process(current_pid) {
                let process_name = process.name();
                let process_exe = process.exe()?.to_string_lossy().to_string();

                if get_shell_name(process_name.to_str()).is_some() {
                    return Some(process_exe);
                }

                if let Some(parent_pid) = process.parent() {
                    current_pid = parent_pid;
                } else {
                    break;
                }
            } else {
                break;
            }
        }
    }

    path
}

fn get_shell_prompt(shell_name: &ShellType, shell_path: &str) -> Option<String> {
    let shell_prompt: Option<String> = match shell_name {
        ShellType::Zsh => {
            let output = Command::new(shell_path)
                .arg("-i")
                .arg("-c")
                .arg("print -P $PS1")
                .output();
            output.ok().and_then(|o| String::from_utf8(o.stdout).ok())
        }
        ShellType::Bash => {
            // Uses parameter transformation; only supported in Bash 4.4+
            let output = Command::new(shell_path).arg("echo \"${PS1@P}\"").output();
            output.ok().and_then(|o| String::from_utf8(o.stdout).ok())
        }
        ShellType::Fish => {
            let output = Command::new(shell_path).arg("fish_prompt").output();
            output.ok().and_then(|o| String::from_utf8(o.stdout).ok())
        }
        ShellType::Csh | ShellType::Tcsh => {
            let output = Command::new(shell_path)
                .arg("-c")
                .arg("echo $prompt")
                .output();
            output.ok().and_then(|o| String::from_utf8(o.stdout).ok())
        }
        ShellType::Pwsh | ShellType::Powershell => {
            let output = Command::new(shell_path)
                .arg("-c")
                .arg("Write-Host $prompt")
                .output();
            output.ok().and_then(|o| String::from_utf8(o.stdout).ok())
        }
    };

    shell_prompt.map(|s| s.trim().to_string())
}

/*
MAIN
*/

pub fn get_shell() -> Shell {
    let path = get_shell_path();
    let name = get_shell_name(path.as_deref());
    let prompt = if let (Some(ref n), Some(ref p)) = (name.as_ref(), path.as_deref()) {
        get_shell_prompt(n, p)
    } else {
        None
    };

    Shell { path, name, prompt }
}
