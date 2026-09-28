const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
  const pythonExecPath = app.isPackaged
    ? path.join(process.resourcesPath, 'python-backend', 'app.exe')
    : path.join(__dirname, 'python-backend', 'app.exe');

  pythonProcess = spawn(pythonExecPath, [], {
    windowsHide: true
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });

  mainWindow = new BrowserWindow({
    width: 900,
    height: 700,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  setTimeout(() => {
    mainWindow.loadURL('http://127.0.0.1:5000');
  }, 2500);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (pythonProcess) {
    try {
      spawn("taskkill", ["/pid", pythonProcess.pid, "/f", "/t"]);
    } catch (e) {
      pythonProcess.kill();
    }
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
