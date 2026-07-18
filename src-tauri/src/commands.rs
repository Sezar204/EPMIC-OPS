use crate::server;
use tauri::{AppHandle, Manager};
#[tauri::command] pub fn start_backend(app: AppHandle) -> Result<(), String> { server::start_backend(&app) }
#[tauri::command] pub fn stop_backend() -> Result<(), String> { server::stop_backend() }
#[tauri::command] pub async fn check_backend_health() -> bool { server::wait_for_backend().await }
#[tauri::command] pub async fn create_backup() -> Result<String, String> { let response = reqwest::Client::new().post("http://127.0.0.1:37210/api/v1/system/backup/now").send().await.map_err(|e| e.to_string())?; response.text().await.map_err(|e| e.to_string()) }
#[tauri::command] pub async fn get_backup_list() -> Result<String, String> { let response = reqwest::get("http://127.0.0.1:37210/api/v1/system/backup/list").await.map_err(|e| e.to_string())?; response.text().await.map_err(|e| e.to_string()) }
#[tauri::command] pub async fn restore_backup(filename: String) -> Result<(), String> { reqwest::Client::new().post("http://127.0.0.1:37210/api/v1/system/backup/restore/".to_owned() + &filename).send().await.map_err(|e| e.to_string())?; Ok(()) }
#[tauri::command] pub fn get_app_data_path(app: AppHandle) -> Result<String, String> { app.path().app_data_dir().map(|p| p.display().to_string()).map_err(|e| e.to_string()) }
#[tauri::command] pub fn open_external_folder(path: String) -> Result<(), String> { tauri::api::process::Command::new("explorer").args([path]).spawn().map_err(|e| e.to_string())?; Ok(()) }

