use std::{process::{Child, Command}, sync::Mutex, time::Duration};
use tauri::AppHandle;
static BACKEND: Mutex<Option<Child>> = Mutex::new(None);
pub fn start_backend(_app: &AppHandle) -> Result<(), String> { let mut backend = BACKEND.lock().map_err(|e| e.to_string())?; if backend.is_some() { return Ok(()); } let executable = if cfg!(windows) { "emicp-backend.exe" } else { "emicp-backend" }; let child = Command::new(executable).spawn().map_err(|e| format!("Unable to start backend: {e}"))?; *backend = Some(child); Ok(()) }
pub fn stop_backend() -> Result<(), String> { let mut backend = BACKEND.lock().map_err(|e| e.to_string())?; if let Some(child) = backend.as_mut() { child.kill().map_err(|e| e.to_string())?; } *backend = None; Ok(()) }
pub async fn wait_for_backend() -> bool { let client = reqwest::Client::new(); for _ in 0..30 { if client.get("http://127.0.0.1:37210/health").send().await.map(|r| r.status().is_success()).unwrap_or(false) { return true; } tokio::time::sleep(Duration::from_secs(1)).await; } false }

