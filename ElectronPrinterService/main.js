const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron');
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const ip = require('ip');

let mainWindow;
let tray = null;
let expressApp;
let server;
const PORT = 5000;
const UPLOAD_DIR = path.join(app.getPath('userData'), 'uploads');

// Ensure upload directory exists
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        show: true,
        title: 'Odoo Printer Service (Electron)',
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    mainWindow.loadFile('index.html');
    
    // Prevent closing, just hide
    mainWindow.on('close', function (event) {
        if (!app.isQuitting) {
            event.preventDefault();
            mainWindow.hide();
        }
        return false;
    });

    mainWindow.webContents.on('did-finish-load', () => {
        updateStatus();
    });
}

function updateStatus() {
    if (mainWindow && !mainWindow.isDestroyed()) {
        const localIp = ip.address();
        mainWindow.webContents.send('update-info', { 
            ip: localIp, 
            port: PORT,
            uploadDir: UPLOAD_DIR
        });
    }
}

function startExpressServer() {
    expressApp = express();
    expressApp.use(cors());
    expressApp.use(express.json());

    // Configure Multer
    const storage = multer.diskStorage({
        destination: function (req, file, cb) {
            cb(null, UPLOAD_DIR)
        },
        filename: function (req, file, cb) {
            // Use original name to preserve extension (important for Odoo)
            // Handle duplicates by overwriting or appending timestamp? 
            // Python service overwrote or handled it. Let's overwrite for simplicity 
            // as Odoo generates unique filenames usually.
            cb(null, file.originalname);
        }
    });
    const upload = multer({ storage: storage });

    // 1. GET /api/printers
    expressApp.get('/api/printers', async (req, res) => {
        try {
            const printers = await mainWindow.webContents.getPrintersAsync();
            const printerNames = printers.map(p => p.name);
            console.log('Printers requested:', printerNames);
            res.json({ success: true, printers: printerNames });
        } catch (error) {
            console.error('Failed to get printers:', error);
            res.status(500).json({ success: false, message: error.message });
        }
    });

    // 2. POST /upload
    expressApp.post('/upload', upload.single('file'), (req, res) => {
        if (!req.file) {
            return res.status(400).json({ success: false, message: 'No file uploaded' });
        }

        console.log(`File uploaded: ${req.file.originalname}`);
        res.json({
            success: true,
            filename: req.file.originalname,
            message: 'File uploaded successfully'
        });
    });

    // 3. POST /print_single
    expressApp.post('/print_single', async (req, res) => {
        const { filename, printer, copies } = req.body;
        console.log(`Print request: ${filename} on ${printer} (${copies} copies)`);

        const filePath = path.join(UPLOAD_DIR, filename);

        if (!fs.existsSync(filePath)) {
            return res.status(404).json({ success: false, message: 'File not found' });
        }

        try {
            printFile(filePath, printer, copies || 1, res);
        } catch (e) {
             console.error('Print error:', e);
             res.status(500).json({ success: false, message: e.message });
        }
    });
    
    // 4. GET /heartbeat
    expressApp.get('/heartbeat', (req, res) => {
        res.json({
            status: 'ok',
            timestamp: new Date().toISOString(),
            service: 'ElectronPrinterService'
        });
    });

    // 5. GET / (Root path for verification)
    expressApp.get('/', (req, res) => {
        res.send('Odoo Electron Printer Service is Running');
    });

    server = expressApp.listen(PORT, '0.0.0.0', () => {
        console.log(`Express server running on port ${PORT}`);
        updateStatus();
    });
    
    server.on('error', (e) => {
        console.error('Server error:', e);
    });
}

function printFile(filePath, printerName, copies, res) {
    let printWin = new BrowserWindow({ 
        show: false, 
        width: 800, 
        height: 600,
        webPreferences: {
            nodeIntegration: true 
        }
    });
    
    const fileUrl = `file://${filePath.replace(/\\/g, '/')}`;
    console.log(`Loading file for printing: ${fileUrl}`);
    
    printWin.loadURL(fileUrl);

    printWin.webContents.on('did-finish-load', () => {
        console.log('File loaded, starting print...');
        
        // Use a slight delay to ensure rendering is complete (especially for large PDFs)
        setTimeout(() => {
            // Use callback style to avoid Promise issues
            printWin.webContents.print({
                silent: true,
                deviceName: printerName,
                copies: parseInt(copies) || 1
            }, (success, errorType) => {
                console.log('Print result:', success, errorType);
                if (success) {
                    if (!res.headersSent) res.json({ success: true, message: 'Printing started' });
                } else {
                    const msg = errorType || 'Unknown error';
                    if (!res.headersSent) res.json({ success: false, message: `Printing failed: ${msg}` });
                }
                
                // Cleanup
                setTimeout(() => {
                    if (!printWin.isDestroyed()) {
                        printWin.close();
                    }
                }, 10000);
            });
        }, 500);
    });
    
    printWin.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
        console.error('Failed to load file:', errorDescription);
        if (!res.headersSent) res.status(500).json({ success: false, message: `Failed to load file: ${errorDescription}` });
        printWin.close();
    });
}

// Network monitoring: Check for IP changes every 10 seconds
setInterval(() => {
    updateStatus();
}, 10000);

app.whenReady().then(() => {
    createWindow();
    startExpressServer();
    
    // Tray setup (commented out until icon is available)
    /*
    tray = new Tray(path.join(__dirname, 'resources', 'icon.png')); 
    const contextMenu = Menu.buildFromTemplate([
        { label: 'Show App', click: () => mainWindow.show() },
        { label: 'Quit', click: () => { app.isQuitting = true; app.quit(); } }
    ]);
    tray.setToolTip('Odoo Printer Service');
    tray.setContextMenu(contextMenu);
    */
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
