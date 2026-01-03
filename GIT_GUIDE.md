# GitHub Repository Management Guide (GitHub 仓库管理指南)

This document describes how to initialize and push this project to GitHub, ensuring sensitive files are ignored.
本文档说明如何将本项目初始化并推送到 GitHub，同时确保忽略敏感文件。

---

## 1. Prerequisites (准备工作)

### Step 0: Configure Identity (配置身份) - Only Once (仅需一次)
If you haven't used Git on this computer before, set your name and email.
如果您是第一次在这台电脑上使用 Git，请先配置您的名字和邮箱。

```bash
# Replace with your GitHub email and name
# 请替换为您自己的 GitHub 邮箱和用户名
git config --global user.email "your_email@example.com"
git config --global user.name "willstardu"
```

Ensure you have Git installed and the `.gitignore` file is created in the project root.
确保您已安装 Git，并且项目根目录下已创建 `.gitignore` 文件。

**Check `.gitignore` content (检查忽略规则):**
```text
# Python / Odoo
*.pyc
__pycache__/
*.log
/data/
/odoo.conf

# Node.js / Electron
node_modules/
dist/
dist_v2/
ElectronPrinterService/dist/
ElectronPrinterService/dist_v2/
ElectronPrinterService/node_modules/
.npmrc

# IDE
.vscode/
.trae/
```

---

## 2. Initialize & Push (初始化与推送)

Run the following commands in your project root terminal (e.g., PowerShell or Git Bash).
在项目根目录终端（如 PowerShell 或 Git Bash）运行以下命令。

### Step 1: Initialize Git Repository (初始化 Git 仓库)
```bash
git init
```

### Step 2: Add Files (添加文件)
This will stage all files *except* those in `.gitignore`.
这将暂存除 `.gitignore` 中指定文件之外的所有文件。
```bash
git add .
```

### Step 3: Commit Changes (提交更改)
```bash
git commit -m "Initial commit: Odoo Electron Printer Service source code"
```

### Step 4: Rename Branch (重命名分支)
GitHub uses `main` as the default branch name.
GitHub 默认使用 `main` 作为主分支名。
```bash
git branch -M main
```

### Step 5: Link to Remote Repository (关联远程仓库)
Replace `<YOUR_REPO_URL>` with your actual GitHub repository URL (e.g., `https://github.com/username/odoo-printer.git`).
将 `<YOUR_REPO_URL>` 替换为您实际的 GitHub 仓库地址。
```bash
git remote add origin <YOUR_REPO_URL>
```

### Step 6: Push to GitHub (推送到 GitHub)
```bash
git push -u origin main
```
**Note (注意):**
*   A browser window may pop up asking you to authorize GitHub. Click **"Sign in with your browser"**.
*   执行此命令后，可能会弹出一个网页窗口要求授权 GitHub 登录，请点击 **"Sign in with your browser"** 完成授权。

---

## 3. Common Git Issues (常见 Git 问题)

*   **Error: `Author identity unknown`**
    *   Solution: Run the commands in **Step 0** to set your email and name, then run `git commit --amend --reset-author` to fix the previous commit.
    *   解决：运行 **Step 0** 中的命令配置邮箱和名字，然后运行 `git commit --amend --reset-author` 修正上一次提交。

*   **Error: `remote origin already exists`**
    *   Solution: `git remote remove origin` then try Step 5 again.
    *   解决：先移除旧关联，再重新添加。

*   **Authentication Failed**
    *   Solution: Ensure you are using a Personal Access Token (PAT) if password authentication is disabled, or use SSH keys.
    *   解决：确保使用个人访问令牌 (PAT) 或 SSH 密钥进行认证。

---

## 4. Advanced: GitLab CI/CD Integration (进阶：与 GitLab CI/CD 配合)

If you are using GitLab in your company, you can automate tests with **"Push to Test"**.
如果你在公司内部使用 GitLab，可以实现**“代码一推，测试自跑”**。

Create a `.gitlab-ci.yml` file in the project root with the following content:
在项目根目录创建一个 `.gitlab-ci.yml` 文件，内容如下：

```yaml
stages:
  - test

# Test Odoo Module (测试 Odoo 模块)
test_odoo_module:
  stage: test
  image: python:3.10
  script:
    - pip install -r requirements.txt
    # Assuming standard Odoo test execution
    # 假设标准的 Odoo 测试执行方式
    - python3 odoo-bin --test-enable --stop-after-init -d test_db -i odoo_printer_service

# Test Electron Service (测试 Electron 服务)
test_electron_service:
  stage: test
  image: node:lts
  script:
    - cd ElectronPrinterService
    - npm install
    # Run linter or unit tests if available
    # 运行代码检查或单元测试
    # - npm test
```
*Note: This is a basic example. You may need to adjust the Docker image and scripts based on your actual CI environment.*
*注意：这是一个基础示例。您可能需要根据实际的 CI 环境调整 Docker 镜像和脚本。*
