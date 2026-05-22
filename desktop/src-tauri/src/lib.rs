use std::process::{Child, Command};
use std::sync::Mutex;

static API_PROCESS: Mutex<Option<Child>> = Mutex::new(None);

fn start_api_server() {
    let mut guard = API_PROCESS.lock().unwrap();
    if guard.is_some() {
        return;
    }

    let python = if cfg!(windows) { "python" } else { "python3" };

    if let Ok(child) = Command::new(python)
        .args([
            "-m",
            "uvicorn",
            "api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ])
        .current_dir(std::env::current_dir().unwrap().parent().unwrap().parent().unwrap())
        .spawn()
    {
        *guard = Some(child);
    }
}

fn stop_api_server() {
    let mut guard = API_PROCESS.lock().unwrap();
    if let Some(mut child) = guard.take() {
        let _ = child.kill();
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    start_api_server();

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .on_window_event(|_window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                stop_api_server();
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
