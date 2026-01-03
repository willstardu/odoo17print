# Odoo Electron Printer Service

This is an Electron-based printer service designed to replace the Python/Flask implementation.

## Prerequisites / 前置条件

1.  **Node.js**: You must install Node.js to run this project.
    *   Download: [https://nodejs.org/](https://nodejs.org/) (LTS version recommended)
    *   Verify installation: `node -v` and `npm -v` in terminal.

## Installation / 安装

Open a terminal in this directory (`ElectronPrinterService`) and run:

```bash
npm install
```

## Running / 运行

To start the service (ensure the Python service on port 5000 is stopped first):

```bash
npm start
```

## Building .exe / 打包

To build a Windows executable:

```bash
npm run dist
```

The output will be in the `dist` folder.

## Features / 功能

*   **Port 5000**: Listens on port 5000 (same as Python service).
*   **API Compatible**: `/api/printers`, `/upload`, `/print_single`.
*   **Silent Printing**: Uses Electron's `webContents.print({ silent: true })`.
*   **Heartbeat**: `/heartbeat` endpoint for Odoo status checks.
*   **Tray Icon**: Minimizes to system tray (requires `resources/icon.png`).
