mod commands; mod server;
use tauri::Manager;
fn main() { tauri::Builder::default().invoke_handler(tauri::generate_handler![commands::start_backend, commands::stop_backend, commands::check_backend_health, commands::create_backup, commands::get_backup_list, commands::restore_backup, commands::get_app_data_path, commands::open_external_folder]).setup(|app| { let handle = app.handle().clone(); tauri::async_runtime::spawn(async move { let _ = server::start_backend(&handle); }); Ok(()) }).on_window_event(|window, event| { if let tauri::WindowEvent::CloseRequested { .. } = event { let _ = server::stop_backend(); let _ = window.app_handle(); } }).run(tauri::generate_context!()).expect("EMICP failed to run"); }

