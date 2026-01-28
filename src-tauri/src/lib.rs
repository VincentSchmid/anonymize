mod sidecar;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            // Start the sidecar on app startup
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                if let Err(e) = sidecar::start_sidecar(&app_handle).await {
                    eprintln!("Failed to start sidecar: {}", e);
                }
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            sidecar::start_backend,
            sidecar::stop_backend,
            sidecar::get_backend_url,
            sidecar::check_backend_health,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
