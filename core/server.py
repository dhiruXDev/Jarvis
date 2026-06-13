import os
import sys
import json
import time
import queue
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import psutil

# Shared queues and states
event_clients = set()
event_clients_lock = threading.Lock()
app_command_queue = None  # Will be mapped to main's command_queue
mic_state = {"active": True}  # True = listening, False = sleeping

# Web server startup synchronization
web_server_ready = threading.Event()
web_server_port = None

# System state tracker for events
status_state = {"state": "idle", "duration": 0}

# ==========================================
# BROADCAST EVENTS TO SSE CLIENTS
# ==========================================
def broadcast_event(event_type, data):
    """Encodes and queues an event to all connected SSE browser clients."""
    payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    
    with event_clients_lock:
        disconnected = []
        for client_queue in event_clients:
            try:
                client_queue.put_nowait(payload)
            except queue.Full:
                pass  # Client slow, ignore or drop
            except Exception:
                disconnected.append(client_queue)
                
        for client in disconnected:
            event_clients.discard(client)

def set_hud_status(state, duration=0):
    """Sets state (idle, listening, processing, speaking) and broadcasts to UI."""
    status_state["state"] = state
    status_state["duration"] = duration
    broadcast_event("status", status_state)

# ==========================================
# CAPTURING STDOUT / STDERR FOR HUD TERMINAL
# ==========================================
class LogRedirector:
    def __init__(self, original_stream):
        self.original_stream = original_stream
        self.lock = threading.Lock()

    def write(self, message):
        try:
            self.original_stream.write(message)
        except UnicodeEncodeError:
            encoding = getattr(self.original_stream, "encoding", "utf-8") or "utf-8"
            safe_message = message.encode(encoding, errors="backslashreplace").decode(encoding)
            self.original_stream.write(safe_message)
        # Standard prints append a newline at the end. Let's send non-empty segments
        clean_msg = message.strip()
        if clean_msg:
            # Broadcast the raw print to the frontend log drawer
            broadcast_event("console_log", clean_msg)

    def flush(self):
        self.original_stream.flush()

    def isatty(self):
        return hasattr(self.original_stream, "isatty") and self.original_stream.isatty()

    def fileno(self):
        if hasattr(self.original_stream, "fileno"):
            return self.original_stream.fileno()
        raise OSError("Stream has no fileno")

# Reconfigure streams to support UTF-8 on Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')
    except Exception:
        pass

# Redirect sys.stdout and sys.stderr
sys.stdout = LogRedirector(sys.stdout)
sys.stderr = LogRedirector(sys.stderr)

# ==========================================
# DYNAMIC SYSTEM STATISTICS POLL LOOP
# ==========================================
def system_stats_worker():
    """Polls CPU, Memory, Disk and Network traffic using psutil and streams via SSE."""
    prev_net_io = psutil.net_io_counters()
    prev_time = time.time()
    
    while True:
        try:
            time.sleep(2.0)
            
            # Fetch CPU, Memory and Disk ratios
            cpu_percent = psutil.cpu_percent()
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Compute network speeds (Upload/Download)
            current_net_io = psutil.net_io_counters()
            current_time = time.time()
            dt = current_time - prev_time
            
            if dt > 0:
                bytes_sent_diff = current_net_io.bytes_sent - prev_net_io.bytes_sent
                bytes_recv_diff = current_net_io.bytes_recv - prev_net_io.bytes_recv
                
                # Convert bytes/sec to Megabits/sec (Mbps)
                upload_mbps = (bytes_sent_diff * 8) / (1024 * 1024 * dt)
                download_mbps = (bytes_recv_diff * 8) / (1024 * 1024 * dt)
            else:
                upload_mbps = 0.0
                download_mbps = 0.0
                
            prev_net_io = current_net_io
            prev_time = current_time
            
            # Combine into a metric payload
            stats = {
                "cpu": cpu_percent,
                "ram": {
                    "used": mem.used,
                    "total": mem.total,
                    "percent": mem.percent
                },
                "disk": {
                    "used": disk.used,
                    "total": disk.total,
                    "percent": disk.percent
                },
                "network": {
                    "upload": upload_mbps,
                    "download": download_mbps
                }
            }
            
            broadcast_event("system_stats", stats)
            
        except Exception as e:
            # We catch to avoid crashing stat thread, redirector prints it to console
            sys.stderr.original_stream.write(f"[System Stats Error] {e}\n")

# ==========================================
# CUSTOM HTTP & SSE REQUEST HANDLER
# ==========================================
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")

class JarvisHttpHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    
    def log_message(self, format, *args):
        # Prevent default console prints of GET/POST requests to keep console output clean
        pass
        
    def do_GET(self):
        # 1. SERVER-SENT EVENTS (SSE) STREAM ENDPOINT
        if self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            # Create unique queue for this browser client session
            client_queue = queue.Queue(maxsize=100)
            with event_clients_lock:
                event_clients.add(client_queue)
                
            # Send initial greeting/current status
            self.wfile.write(f"event: status\ndata: {json.dumps(status_state)}\n\n".encode())
            self.wfile.flush()
            
            # Yield events to client as they arrive
            try:
                while True:
                    try:
                        event_data = client_queue.get(timeout=15)
                        self.wfile.write(event_data.encode())
                        self.wfile.flush()
                    except queue.Empty:
                        # Send a keepalive comment line to keep the TCP/HTTP connection open
                        self.wfile.write(b": keepalive\n\n")
                        self.wfile.flush()
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                pass
            finally:
                with event_clients_lock:
                    event_clients.discard(client_queue)
            return

        # 2. STATIC FILES SERVING FROM /frontend/dist
        # Normalize and map paths safely, stripping query strings
        rel_path = self.path.lstrip("/")
        if not rel_path or rel_path == "":
            rel_path = "index.html"
            
        safe_rel = rel_path.split("?")[0]
        file_path = os.path.normpath(os.path.join(FRONTEND_DIR, safe_rel))
        
        # Ensure request does not traverse out of the frontend dist folder
        if file_path.lower().startswith(FRONTEND_DIR.lower()) and os.path.exists(file_path) and os.path.isfile(file_path):
            print(f"[SERVER] Serving static file: {file_path}")
            self.send_response(200)
            
            # Handle mime types
            if file_path.endswith(".html"):
                self.send_header("Content-Type", "text/html")
            elif file_path.endswith(".css"):
                self.send_header("Content-Type", "text/css")
            elif file_path.endswith(".js"):
                self.send_header("Content-Type", "application/javascript")
            elif file_path.endswith(".svg"):
                self.send_header("Content-Type", "image/svg+xml")
            elif file_path.endswith(".mp3"):
                self.send_header("Content-Type", "audio/mpeg")
            else:
                self.send_header("Content-Type", "application/octet-stream")
                
            file_size = os.path.getsize(file_path)
            self.send_header("Content-Length", str(file_size))
            self.end_headers()
            
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
            self.wfile.flush()
        else:
            self.send_error(404, "File Not Found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        # 1. API: RECEIVE COMMAND FROM KEYBOARD VIEW
        if self.path == "/api/command":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode("utf-8"))
                cmd = data.get("command", "").strip()
                
                if cmd and app_command_queue:
                    # Enqueue the command into main queue for execution
                    app_command_queue.put(cmd)
                    
                    response_data = json.dumps({"status": "success"}).encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(response_data)))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_data)
                    self.wfile.flush()
                else:
                    response_data = json.dumps({"status": "error", "message": "Empty command"}).encode()
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(response_data)))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_data)
                    self.wfile.flush()
            except Exception as e:
                response_data = json.dumps({"status": "error", "message": str(e)}).encode()
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response_data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(response_data)
                self.wfile.flush()
            return
            
        # 2. API: TOGGLE MICROPHONE LISTENING STATE
        elif self.path == "/api/toggle-mic":
            mic_state["active"] = not mic_state["active"]
            
            response_data = json.dumps({"status": "success", "active": mic_state["active"]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response_data)
            self.wfile.flush()
            return
            
        # 3. API: TRIGGER STARTUP GREETING WHEN FRONTEND IS READY
        elif self.path == "/api/ready":
            from core.speaker import speak
            speak("Hey Boss, I'm ready. I'm Jarvis, your personal AI assistant. All systems are online and waiting for your command.")
            
            response_data = json.dumps({"status": "success"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response_data)
            self.wfile.flush()
            return
            
        self.send_error(404, "Not Found")

# ==========================================
# SERVER INITIALIZER & BOOT
# ==========================================
def run_web_server(port, command_queue):
    global app_command_queue
    app_command_queue = command_queue
    
    server_address = ("", port)
    
    # Run the system stats background monitor
    stats_thread = threading.Thread(target=system_stats_worker, daemon=True)
    stats_thread.start()
    
    # Try finding an available port if 8000 is occupied
    httpd = None
    global web_server_port
    for current_port in range(port, port + 20):
        try:
            httpd = ThreadingHTTPServer(("", current_port), JarvisHttpHandler)
            web_server_port = current_port
            web_server_ready.set()
            # Log the original stdout
            sys.stdout.original_stream.write(f"\n[SYSTEM] Futuristic UI Web Server online at http://localhost:{current_port}\n")
            break
        except OSError:
            continue
            
    if not httpd:
        sys.stderr.original_stream.write("[FATAL ERROR] Could not allocate port for Web Server.\n")
        return
        
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
