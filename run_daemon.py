import os
import sys
import time
import subprocess
from datetime import datetime

# Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WSGI_PATH = os.path.join(BASE_DIR, 'backend', 'wsgi.py')
PYTHON_EXE = os.path.join(BASE_DIR, '.venv', 'Scripts', 'python.exe')
LOG_FILE = os.path.join(BASE_DIR, 'server_logs.txt')

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [Daemon] {message}\n"
    print(log_line, end="")
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
    except Exception as e:
        sys.stderr.write(f"Failed to write to log file: {e}\n")

def run_server():
    log_message("Starting AgriVistara production daemon...")
    log_message(f"Target python: {PYTHON_EXE}")
    log_message(f"Target WSGI: {WSGI_PATH}")
    log_message(f"Logging to: {LOG_FILE}")
    
    consecutive_failures = 0
    
    while True:
        start_time = time.time()
        
        try:
            log_message("Launching production server process using Waitress WSGI...")
            # Run python unbuffered (-u) so logs are written immediately
            process = subprocess.Popen(
                [PYTHON_EXE, '-u', WSGI_PATH],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=BASE_DIR
            )
            
            # Read stdout/stderr line-by-line and write to daemon output/logs
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                # Append server output directly to log file
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_line = f"[{timestamp}] [Server] {line}"
                print(log_line, end="")
                try:
                    with open(LOG_FILE, 'a', encoding='utf-8') as f:
                        f.write(log_line)
                except:
                    pass
            
            # Wait for process exit status
            return_code = process.wait()
            log_message(f"Server process exited with return code: {return_code}")
            
        except Exception as e:
            log_message(f"Exception raised while running server: {e}")
            return_code = -1
            
        run_duration = time.time() - start_time
        
        if run_duration < 8.0:
            consecutive_failures += 1
            delay = min(30, 2 ** consecutive_failures)
            log_message(f"Server crashed/exited too quickly ({run_duration:.2f}s). Suspending restart for {delay}s...")
            time.sleep(delay)
        else:
            consecutive_failures = 0
            log_message("Server exited, restarting immediately...")
            time.sleep(1)

if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        log_message("Daemon stopped by user keyboard interrupt.")
    except Exception as e:
        log_message(f"Daemon crashed: {e}")
