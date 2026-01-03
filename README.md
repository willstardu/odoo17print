# Odoo 17 Local Printer Integration (Odoo 17 本地打印集成方案)

This project provides a solution to print documents from Odoo (Web) directly to local Windows printers without user interaction (Silent Printing).
本项目提供了一个解决方案，允许 Odoo（网页端）直接调用本地 Windows 打印机进行静默打印，无需用户手动选择打印机。

---

## 1. System Architecture (系统架构)

The system consists of two main components:
系统由两个主要部分组成：

1.  **Electron Printer Service (Client-Side)**:
    *   Runs on the Windows computer connected to the printers.
    *   Acts as a local web server (Port 5000).
    *   Receives print requests from Odoo and sends them to the printer driver.
    *   **客户端（Windows）**：运行在连接打印机的电脑上，作为本地服务器（端口 5000），接收 Odoo 的打印请求并发送给打印机驱动。

2.  **Odoo Printer Module (Server-Side)**:
    *   Installed in Odoo.
    *   Manages printer servers and printer lists.
    *   Sends documents (PDF/ZPL) to the Electron service.
    *   **服务端（Odoo）**：安装在 Odoo 中，管理打印服务器和打印机列表，将文档发送给 Electron 服务。

---

## 2. Deployment Guide (部署指南)

### Part A: Windows Client Deployment (Windows 客户端部署)

**Prerequisites (环境要求):**
*   Windows 10/11
*   Node.js (LTS Version) - *Only for development/building (仅开发/打包需要)*

**Steps (步骤):**

1.  **Install the Service (安装服务):**
    *   Navigate to `ElectronPrinterService/dist/`.
    *   Run `odoo-electron-printer-service Setup 1.0.0.exe`.
    *   The app will launch automatically.
    *   运行 `ElectronPrinterService/dist/` 目录下的安装包 `Setup 1.0.0.exe`，程序会自动启动。

2.  **Verify Running Status (验证运行状态):**
    *   Open browser and go to `http://localhost:5000`.
    *   You should see: **"Odoo Electron Printer Service is Running"**.
    *   打开浏览器访问 `http://localhost:5000`，应显示服务正在运行。

3.  **Check IP Address (检查 IP 地址):**
    *   Note down the IP address of this computer (e.g., `192.168.0.106`).
    *   记录本机 IP 地址（如 `192.168.0.106`），后续配置 Odoo 需要用到。

### Part B: Odoo Module Installation (Odoo 模块安装)

1.  **Install Module (安装模块):**
    *   Copy `odoo_printer_service` folder to your Odoo `addons` directory.
    *   Restart Odoo service.
    *   Go to **Apps**, update app list, and install "Printer Service".
    *   将 `odoo_printer_service` 文件夹复制到 Odoo 的 `addons` 目录，重启 Odoo，并在应用列表中安装 "Printer Service"。

2.  **Configure Connection (配置连接):**
    *   Go to **Printer Service** App -> **Servers**.
    *   Edit the "Local Printer Server".
    *   **Server URL**: `http://<WINDOWS_IP>:5000` (e.g., `http://192.168.0.106:5000`).
    *   Click **Check Status** (Should be Online).
    *   Click **Fetch Printers** (Should list your Windows printers).
    *   进入 **Printer Service** 应用 -> **Servers**，编辑服务器配置，填入 Windows 电脑的 IP 地址，点击“检查状态”和“获取打印机”。

### Part C: Building from Source (源码构建/开发指南)

If you need to modify the code or rebuild the exe, follow these steps to avoid network issues in China.
如果您需要修改代码或重新打包，请按照以下步骤操作，以避免国内网络问题。

**0. Environment Setup (环境准备)**

Before you start, you need to install Node.js.
在开始之前，您需要先安装 Node.js。

1.  **Install Node.js (包含 npm)**:
    *   Visit [nodejs.org](https://nodejs.org) and download the **LTS (Long Term Support)** version. (访问官网下载 LTS 长期支持版，这是最稳定的版本)
    *   Run the installer and click "Next". (运行安装程序)
    *   **Crucial**: Ensure **"Add to PATH"** is selected (default). (关键点：确保勾选 "Add to PATH"，这会自动配置环境变量)
    *   Recommended: Check **"Automatically install the necessary tools"** to install C++ build tools. (建议勾选自动安装必要工具)

2.  **Verify Installation (验证安装)**:
    *   Restart your terminal (PowerShell/CMD). (安装完成后必须重启终端)
    *   Run `node -v` and `npm -v`.
    *   If you see version numbers (e.g., v20.x.x), installation is successful. (如果看到版本号，说明安装成功)

**1. Clean Install & Configure Mirrors (清理缓存并配置国内镜像):**

Run these commands in PowerShell (Administrator recommended) to set up the environment correctly.
建议在 PowerShell（管理员模式）下运行以下命令，以确保环境配置正确。

```powershell
# 1. Force clean npm cache (强制清理 npm 缓存)
npm cache clean --force

# 2. Configure domestic mirrors (配置国内镜像源)
# Write configuration to .npmrc file (写入配置文件)
Add-Content .npmrc "electron_mirror=https://npmmirror.com/mirrors/electron/`n"
Add-Content .npmrc "electron_builder_binaries_mirror=https://npmmirror.com/mirrors/electron-builder-binaries/`n"
Add-Content .npmrc "registry=https://registry.npmmirror.com`n"

# 3. Remove existing node_modules (删除可能损坏的依赖文件夹)
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue

# 4. Install dependencies (重新安装依赖)
npm install

# Optional: If download hangs, use verbose mode to debug
# 可选：如果下载卡住，使用详细模式查看进度
# npm install --verbose
```

**2. Run in Development Mode (开发模式运行):**

```bash
npm start
```

**3. Build Executable (打包生成 EXE):**

```bash
npm run dist
```
*   The output file will be in the `dist` folder (e.g., `odoo-electron-printer-service Setup 1.0.0.exe`).
*   打包后的文件位于 `dist` 目录中。

---

## 3. Source Code Explanation (核心代码解析)

### A. Electron Main Process (`main.js`)
*Responsible for handling HTTP requests and printing.*
*负责处理 HTTP 请求并调用打印机。*

```javascript
// 1. Start Express Server (启动 Web 服务器)
function startExpressServer() {
    expressApp = express();
    // ... middleware setup ...

    // API: Fetch Printer List (获取打印机列表接口)
    expressApp.get('/api/printers', async (req, res) => {
        // Use Electron's API to get system printers
        // 调用 Electron 原生 API 获取系统打印机
        const printers = await mainWindow.webContents.getPrintersAsync();
        res.json({ success: true, printers: printers.map(p => p.name) });
    });

    // API: Print Single File (单文件打印接口)
    expressApp.post('/print_single', async (req, res) => {
        const { filename, printer, copies } = req.body;
        const filePath = path.join(UPLOAD_DIR, filename); // File path from upload
        
        // Call the silent printing function
        // 调用静默打印函数
        printFile(filePath, printer, copies || 1, res);
    });
}

// 2. Silent Printing Logic (静默打印逻辑)
function printFile(filePath, printerName, copies, res) {
    // Create a hidden window (创建一个隐藏窗口)
    let printWin = new BrowserWindow({ show: false });
    
    // Load the file (PDF/Image/HTML) into the window
    // 加载文件到窗口中
    printWin.loadURL(`file://${filePath}`);

    printWin.webContents.on('did-finish-load', () => {
        // Execute printing (执行打印)
        // Use callback style (使用回调方式)
        printWin.webContents.print({
            silent: true,            // No dialog (无弹窗)
            deviceName: printerName, // Target printer (目标打印机)
            copies: copies
        }, (success, errorType) => {
            // Return result to Odoo (返回结果给 Odoo)
            if (success) {
                res.json({ success: true });
            } else {
                res.json({ success: false, message: errorType });
            }
            
            // Cleanup
            printWin.close();
        });
    });
}
```

### B. Odoo Model (`models/print_server.py`)
*Manages connection and sends requests.*
*管理连接并发送请求。*

```python
class PrinterServer(models.Model):
    _name = 'printer.server'

    # Configuration fields (配置字段)
    url = fields.Char(default='http://localhost:5000')
    status = fields.Selection([('online', 'Online'), ('offline', 'Offline')], default='unknown')

    def action_check_status(self):
        """
        Heartbeat Check (心跳检测)
        Sends a request to /heartbeat to check if the Electron service is alive.
        发送请求到 /heartbeat 检查 Electron 服务是否在线。
        """
        try:
            url = f"{self.url.rstrip('/')}/heartbeat"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                self.status = 'online'
            else:
                self.status = 'offline'
        except Exception:
            self.status = 'offline'

    def action_fetch_printers(self):
        """
        Fetch Printers (获取打印机)
        Gets the list of printers from the Electron service and creates records in Odoo.
        从 Electron 服务获取打印机列表并在 Odoo 中创建记录。
        """
        api_url = f"{self.url.rstrip('/')}/api/printers"
        response = requests.get(api_url, timeout=5)
        data = response.json()
        
        if data.get('success'):
            # Update local printer records
            # 更新本地打印机记录
            for p_name in data.get('printers', []):
                self.env['printer.server.printer'].create({
                    'name': p_name, 
                    'server_id': self.id
                })
```

---

## 4. Troubleshooting (常见问题排查)

| Issue (问题) | Possible Cause (可能原因) | Solution (解决方案) |
| :--- | :--- | :--- |
| **Status Offline** (状态离线) | Wrong IP address in Odoo (Odoo 中 IP 填写错误) | Check Windows IP via `ipconfig` and update Odoo Server URL. (检查 Windows IP 并更新 Odoo 设置) |
| **Fetch Failed** (获取失败) | Firewall blocking port 5000 (防火墙拦截) | Allow Node.js/Electron through Windows Firewall on port 5000. (允许端口 5000 通行) |
| **Print Error** (打印报错) | Printer driver issue (驱动问题) | Ensure you can print a test page from Windows first. (确保 Windows 本身能打印测试页) |
