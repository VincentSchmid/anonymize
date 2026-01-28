//! Sidecar management for the Python anonymization API.

use serde::{Deserialize, Serialize};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Mutex;
use tauri::AppHandle;
use tauri_plugin_shell::process::CommandChild;
use tauri_plugin_shell::ShellExt;
use tokio::time::{sleep, Duration};

/// The port the sidecar API runs on.
const SIDECAR_PORT: u16 = 14200;

/// Maximum time to wait for the sidecar to become healthy.
const HEALTH_CHECK_TIMEOUT_SECS: u64 = 30;

/// Interval between health check attempts.
const HEALTH_CHECK_INTERVAL_MS: u64 = 500;

/// Global state for the sidecar process.
static SIDECAR_RUNNING: AtomicBool = AtomicBool::new(false);
static SIDECAR_PROCESS: Mutex<Option<CommandChild>> = Mutex::new(None);

#[derive(Debug, Serialize, Deserialize)]
pub struct HealthResponse {
    pub status: String,
    pub model_loaded: bool,
    pub version: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct BackendStatus {
    pub running: bool,
    pub healthy: bool,
    pub url: String,
}

/// Start the sidecar process.
pub async fn start_sidecar(app: &AppHandle) -> Result<(), String> {
    if SIDECAR_RUNNING.load(Ordering::SeqCst) {
        return Ok(());
    }

    println!("Starting anonymize-api sidecar...");

    let shell = app.shell();
    let sidecar = shell
        .sidecar("anonymize-api")
        .map_err(|e| format!(
            "Failed to create sidecar command: {}. \
            The sidecar binary 'anonymize-api' may be missing from the installation.",
            e
        ))?;

    let (mut rx, child) = sidecar.spawn().map_err(|e| {
        format!(
            "Failed to start the backend service: {}. \
            Possible causes: (1) The executable may be blocked by antivirus software, \
            (2) Required system libraries may be missing, \
            (3) The application may not have permission to run executables. \
            Try running the application as administrator or check your antivirus settings.",
            e
        )
    })?;

    // Store the child process
    {
        let mut process = SIDECAR_PROCESS.lock().map_err(|e| e.to_string())?;
        *process = Some(child);
    }

    SIDECAR_RUNNING.store(true, Ordering::SeqCst);

    // Spawn a task to handle sidecar output
    tauri::async_runtime::spawn(async move {
        use tauri_plugin_shell::process::CommandEvent;
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    println!("[sidecar] {}", String::from_utf8_lossy(&line));
                }
                CommandEvent::Stderr(line) => {
                    eprintln!("[sidecar] {}", String::from_utf8_lossy(&line));
                }
                CommandEvent::Terminated(payload) => {
                    println!("[sidecar] Terminated with code: {:?}", payload.code);
                    SIDECAR_RUNNING.store(false, Ordering::SeqCst);
                    break;
                }
                CommandEvent::Error(e) => {
                    eprintln!("[sidecar] Error: {}", e);
                }
                _ => {}
            }
        }
    });

    // Wait for the sidecar to become healthy
    wait_for_health().await?;

    println!("Sidecar started successfully on port {}", SIDECAR_PORT);
    Ok(())
}

/// Stop the sidecar process.
pub fn stop_sidecar() -> Result<(), String> {
    if !SIDECAR_RUNNING.load(Ordering::SeqCst) {
        return Ok(());
    }

    println!("Stopping sidecar...");

    let mut process = SIDECAR_PROCESS.lock().map_err(|e| e.to_string())?;
    if let Some(child) = process.take() {
        child.kill().map_err(|e| format!("Failed to kill sidecar: {}", e))?;
    }

    SIDECAR_RUNNING.store(false, Ordering::SeqCst);
    println!("Sidecar stopped");
    Ok(())
}

/// Wait for the sidecar to become healthy.
async fn wait_for_health() -> Result<(), String> {
    let url = format!("http://127.0.0.1:{}/health", SIDECAR_PORT);
    let start = std::time::Instant::now();
    let timeout = Duration::from_secs(HEALTH_CHECK_TIMEOUT_SECS);

    while start.elapsed() < timeout {
        match check_health_internal(&url).await {
            Ok(health) if health.model_loaded => {
                println!("Sidecar is healthy (version: {})", health.version);
                return Ok(());
            }
            Ok(_) => {
                println!("Sidecar responding but model not yet loaded...");
            }
            Err(_) => {
                // Sidecar not yet responding
            }
        }
        sleep(Duration::from_millis(HEALTH_CHECK_INTERVAL_MS)).await;
    }

    Err(format!(
        "Backend service failed to start within {} seconds. \
        The service may have crashed during startup. \
        Check if port {} is already in use by another application, \
        or if there are missing dependencies (Python runtime, spaCy model).",
        HEALTH_CHECK_TIMEOUT_SECS,
        SIDECAR_PORT
    ))
}

/// Internal health check using reqwest-like functionality.
async fn check_health_internal(_url: &str) -> Result<HealthResponse, String> {
    // Use a simple TCP connection and HTTP request
    use std::io::{Read, Write};
    use std::net::TcpStream;
    use std::time::Duration;

    let addr = format!("127.0.0.1:{}", SIDECAR_PORT);
    let mut stream = TcpStream::connect_timeout(
        &addr.parse().map_err(|e| format!("Invalid address: {}", e))?,
        Duration::from_secs(2),
    )
    .map_err(|e| format!("Connection failed: {}", e))?;

    stream
        .set_read_timeout(Some(Duration::from_secs(5)))
        .map_err(|e| format!("Failed to set timeout: {}", e))?;

    let request = format!(
        "GET /health HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nConnection: close\r\n\r\n",
        SIDECAR_PORT
    );

    stream
        .write_all(request.as_bytes())
        .map_err(|e| format!("Failed to send request: {}", e))?;

    let mut response = String::new();
    stream
        .read_to_string(&mut response)
        .map_err(|e| format!("Failed to read response: {}", e))?;

    // Parse the response body (skip headers)
    let body = response
        .split("\r\n\r\n")
        .nth(1)
        .ok_or("Invalid HTTP response")?;

    serde_json::from_str(body).map_err(|e| format!("Failed to parse response: {}", e))
}

// Tauri commands

#[tauri::command]
pub async fn start_backend(app: AppHandle) -> Result<BackendStatus, String> {
    start_sidecar(&app).await?;
    Ok(BackendStatus {
        running: true,
        healthy: true,
        url: format!("http://127.0.0.1:{}", SIDECAR_PORT),
    })
}

#[tauri::command]
pub fn stop_backend() -> Result<(), String> {
    stop_sidecar()
}

#[tauri::command]
pub fn get_backend_url() -> String {
    format!("http://127.0.0.1:{}", SIDECAR_PORT)
}

#[tauri::command]
pub async fn check_backend_health() -> Result<BackendStatus, String> {
    let url = format!("http://127.0.0.1:{}/health", SIDECAR_PORT);
    match check_health_internal(&url).await {
        Ok(health) => Ok(BackendStatus {
            running: SIDECAR_RUNNING.load(Ordering::SeqCst),
            healthy: health.model_loaded,
            url: format!("http://127.0.0.1:{}", SIDECAR_PORT),
        }),
        Err(_) => Ok(BackendStatus {
            running: SIDECAR_RUNNING.load(Ordering::SeqCst),
            healthy: false,
            url: format!("http://127.0.0.1:{}", SIDECAR_PORT),
        }),
    }
}
