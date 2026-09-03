#[tauri::command]
fn get_shell_status() -> String {
    "QROS_PHASE4_LOCAL_ONLY".to_string()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![get_shell_status])
        .run(tauri::generate_context!())
        .expect("QUT desktop shell failed to start");
}
