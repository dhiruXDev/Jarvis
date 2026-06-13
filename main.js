const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let mainWindow;
let pythonProcess = null;
let serverPort = null;
let isServerOnline = false;

// Create standard Electron window
function createMainWindow(url) {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    title: 'JARVIS - Futuristic AI Command Center',
    icon: path.join(__dirname, 'assets', 'icon.ico'),
    backgroundColor: '#020713',
    show: false, // Show once ready to avoid white flash
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true
    }
  });

  // Load the web server URL
  mainWindow.loadURL(url);

  // Optimize window showing
  mainWindow.once('ready-to-show', () => {
    mainWindow.maximize();
    mainWindow.show();
  });

  // Disable default menu bar for clean dashboard feel
  Menu.setApplicationMenu(null);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Create an error window to show Python crash logs
function createErrorWindow(errorMsg) {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    title: 'JARVIS - Backend Connection Error',
    icon: path.join(__dirname, 'assets', 'icon.ico'),
    backgroundColor: '#020713',
    webPreferences: {
      nodeIntegration: true, // Allow node integration in the error page for error passing
      contextIsolation: false
    }
  });

  // Create temporary error.html with the error details if it doesn't exist, or write it directly
  const htmlPath = path.join(__dirname, 'error.html');
  mainWindow.loadFile(htmlPath).then(() => {
    mainWindow.webContents.send('backend-error', errorMsg);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Start Python backend
function startPythonBackend() {
  return new Promise((resolve, reject) => {
    // Check if python backend is already running (e.g. launched main.py directly)
    if (process.env.JARVIS_PORT) {
      serverPort = process.env.JARVIS_PORT;
      isServerOnline = true;
      console.log(`[Electron] Connecting to existing Python backend on port ${serverPort}`);
      resolve(`http://localhost:${serverPort}`);
      return;
    }

    // Relative path to local Python virtual environment interpreter
    const pythonBin = path.join(__dirname, '.venv', 'Scripts', 'python.exe');
    const mainPy = path.join(__dirname, 'main.py');

    if (!fs.existsSync(pythonBin)) {
      reject(`Python virtual environment not found at: ${pythonBin}\nPlease make sure to run setup and create .venv first.`);
      return;
    }

    console.log(`[Electron] Launching Python backend: ${pythonBin} -u ${mainPy}`);
    
    // Spawn with -u for unbuffered output to receive stdout instantly
    pythonProcess = spawn(pythonBin, ['-u', mainPy], {
      cwd: __dirname,
      env: { ...process.env, PYTHONUNBUFFERED: '1', ELECTRON_RUNNING: '1' }
    });

    let stderrLogs = '';
    let startTimeout = setTimeout(() => {
      if (!isServerOnline) {
        console.error('[Electron] Python startup timed out.');
        pythonProcess.kill();
        reject('Backend startup timed out (20 seconds). Stderr logs:\n' + stderrLogs);
      }
    }, 20000);

    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`[Python STDOUT] ${output.trim()}`);

      // Search for the online token print from server.py
      const match = output.match(/Futuristic UI Web Server online at http:\/\/localhost:(\d+)/i);
      if (match) {
        serverPort = match[1];
        isServerOnline = true;
        clearTimeout(startTimeout);
        resolve(`http://localhost:${serverPort}`);
      }
    });

    pythonProcess.stderr.on('data', (data) => {
      const errStr = data.toString();
      console.error(`[Python STDERR] ${errStr.trim()}`);
      stderrLogs += errStr;
    });

    pythonProcess.on('close', (code) => {
      console.log(`[Electron] Python process exited with code ${code}`);
      clearTimeout(startTimeout);
      if (!isServerOnline) {
        reject(`Python process crashed with code ${code}.\nTraceback/Errors:\n${stderrLogs}`);
      } else {
        // Backend crashed after being online
        if (mainWindow) {
          createErrorWindow(`Python process crashed unexpectedly with code ${code}.\nTraceback:\n${stderrLogs}`);
        }
      }
    });
  });
}

app.whenReady().then(() => {
  startPythonBackend()
    .then((url) => {
      console.log(`[Electron] Server is online. Loading frontend from ${url}`);
      createMainWindow(url);
    })
    .catch((err) => {
      console.error(`[Electron] Failed to start backend:`, err);
      createErrorWindow(err);
    });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      if (isServerOnline) {
        createMainWindow(`http://localhost:${serverPort}`);
      }
    }
  });
});

app.on('window-all-closed', () => {
  // Quit app and kill Python backend
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  if (pythonProcess) {
    console.log('[Electron] Killing Python process...');
    pythonProcess.kill();
  }
});

ipcMain.on('relaunch', () => {
  app.relaunch();
  app.exit(0);
});
