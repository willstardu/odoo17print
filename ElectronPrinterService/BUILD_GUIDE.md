# Electron Build Guide & Troubleshooting (Electron 打包指南与常见问题)

This document provides detailed instructions and troubleshooting tips for building the Electron Printer Service into an executable (.exe) file.
本文档提供 Electron 打印服务打包成可执行文件 (.exe) 的详细指南和常见问题排查技巧。

---

## 1. Prerequisites (打包前准备)

Before building, ensure you have:
在打包之前，请确保您已经：

1.  **Stopped the running service** (停止正在运行的服务):
    *   Press `Ctrl + C` in the terminal to stop `npm start`.
    *   Ensure no background processes are running (Check Task Manager for `electron.exe` or `odoo-electron-printer-service.exe`).
    *   按 `Ctrl + C` 停止 `npm start`，并检查任务管理器确保没有后台进程。

2.  **Configured Mirrors** (配置国内镜像):
    *   Essential for users in China to avoid download timeouts.
    *   Ensure your `.npmrc` file is configured (see main README).
    *   必须配置国内镜像（如 npmmirror），否则下载 Electron 二进制文件极易超时失败。

---

## 2. Standard Build Command (标准打包命令)

Run the following command in the `ElectronPrinterService` directory:
在 `ElectronPrinterService` 目录下运行以下命令：

```bash
npm run dist
```

*   **Output Location (输出位置)**: `ElectronPrinterService/dist/`
*   **File Name (文件名)**: `odoo-electron-printer-service Setup 1.0.0.exe`

---

## 3. Common Errors & Solutions (常见错误与解决方案)

### Error 1: "The process cannot access the file" / "EPERM: operation not permitted"
**Error Message (报错信息)**:
`remove ...\dist\win-unpacked\resources\app.asar: The process cannot access the file because it is being used by another process.`

**Cause (原因)**:
Files in the `dist` folder are locked by a previous process (e.g., a crashed build or a running instance of the app).
`dist` 文件夹中的文件被之前的进程（如崩溃的打包进程或正在运行的程序）锁定，无法删除。

**Solution (解决方案)**:

**Method A: Force Kill Processes (方法 A：强制杀进程)**
Run these commands in PowerShell to kill all related processes:
在 PowerShell 中运行以下命令杀掉所有相关进程：
```powershell
taskkill /F /IM electron.exe /T
taskkill /F /IM odoo-electron-printer-service.exe /T
```
Then try `npm run dist` again.
然后重试 `npm run dist`。

**Method B: Build to a New Directory (方法 B：打包到新目录)**
If the folder is still locked, you can tell the builder to use a different output folder (e.g., `dist_v2`) to bypass the lock:
如果文件夹依然被锁定，可以直接指定一个新的输出目录（如 `dist_v2`）来绕过锁定：
```bash
npx electron-builder --config.directories.output=dist_v2
```
*The exe will be generated in `dist_v2` folder.*

**Method C: Restart Computer (方法 C：重启电脑)**
The ultimate solution to release all file locks.
重启电脑是释放所有文件锁的终极方案。

---

### Error 2: Download Timeout / Connection Error
**Error Message (报错信息)**:
`Get "https://github.com/.../electron-...zip": dial tcp ...: i/o timeout`

**Cause (原因)**:
Network issues connecting to GitHub to download Electron binaries.
连接 GitHub 下载 Electron 二进制文件时网络超时。

**Solution (解决方案)**:
Ensure your `.npmrc` file contains the mirror configuration:
确保项目根目录下的 `.npmrc` 文件包含以下镜像配置：

```ini
electron_mirror=https://npmmirror.com/mirrors/electron/
electron_builder_binaries_mirror=https://npmmirror.com/mirrors/electron-builder-binaries/
```

---

### Error 3: Icon Not Found
**Error Message (报错信息)**:
`default Electron icon is used reason=application icon is not set`

**Cause (原因)**:
You haven't provided a custom icon file (`icon.png` or `icon.ico`).
未提供自定义图标文件。

**Solution (解决方案)**:
1.  Place an `icon.png` (at least 256x256) in the `ElectronPrinterService` directory.
2.  Re-run `npm run dist`.
1.  在 `ElectronPrinterService` 目录下放置一个 `icon.png`（建议至少 256x256）。
2.  重新运行 `npm run dist`。

---

## 4. Best Practices (最佳实践)

1.  **Clean Build (纯净构建)**:
    Before a final release, it's good practice to delete the `dist` folder manually to ensure a fresh build.
    发布正式版前，建议手动删除 `dist` 文件夹以确保构建纯净。
    ```powershell
    Remove-Item -Recurse -Force dist
    ```

2.  **Version Management (版本管理)**:
    Update the `version` field in `package.json` (e.g., change `"1.0.0"` to `"1.0.1"`) before building a new update.
    每次更新前，记得修改 `package.json` 中的 `version` 字段（如改为 `1.0.1`）。
