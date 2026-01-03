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

## 3. Routine Updates: The Standard Trilogy (日常更新：标准更新三步曲)

Whenever you finish a feature or fix a bug, follow these 3 steps in order:
每当你完成了一个小功能或修复了一个 Bug，请依次执行：

### Step 1: Add (装箱)
Tell Git which file changes to include.
告诉 Git 哪些文件变动要包含进去。
```bash
git add .
# . represents all changes in current directory
# . 代表当前目录下所有变动，你也可以指定单个文件 git add main.js
```

### Step 2: Commit (封箱)
Label this update and record what you did.
给这次更新贴上标签，记录你做了什么。
```bash
git commit -m "Fixed printer connection timeout bug"
# "修复了打印机连接超时的Bug"
```
*`-m` follows your description, which is very important for future reference. (`-m` 后面是你的说明，非常重要，方便以后翻旧账)*

### Step 3: Push (发货)
Push local records to the GitHub server.
把本地的记录推送到 GitHub 服务器。
```bash
git push
```

### FAQ: Why can't I just use `git push`? (为什么不能只用 git push？)
If you run `git push` directly:
如果你直接运行 `git push`：

1.  **No Commit**: Git will say `Everything up-to-date` because the local repository hasn't recorded your new code yet.
    *   如果你没有执行 commit，Git 会提示 `Everything up-to-date`（因为本地仓库还没记录下你的新代码）。
2.  **Already Committed**: `git push` will send all your "sealed but not shipped" boxes to GitHub at once.
    *   如果你已经执行过 commit，那么 `git push` 会把你本地所有“封好了但还没发走”的箱子全部一次性发往 GitHub。

### Shortcuts (快捷小技巧)
If you find three lines too troublesome, use a compound command in the Trae terminal:
如果你嫌三行命令太麻烦，可以在 Trae 终端使用复合命令（一行搞定）：

**Windows (PowerShell):**
```powershell
git add .; git commit -m "Quick update"; git push
```

**Mac/Linux/Bash:**
```bash
git add . && git commit -m "Quick update" && git push
```

---

## 4. Expert Workflow for Trae Users (专家建议：避坑工作流)

Since you are using Trae (where AI modifies code extensively), it is recommended to develop the habit of "Pull -> Write -> Push" to prevent code conflicts.
因为你在使用 Trae（AI 会大面积修改代码），建议养成 “先拉、再写、后推” 的习惯，防止代码冲突：

| Step | Command (命令) | Action Description (动作描述) |
| :--- | :--- | :--- |
| **1. 拿货** | `git pull` | Before starting, pull the latest code from GitHub. <br> 开始写代码前，先从 GitHub 拉取最新的代码（防止别人改了或者你在另一台电脑改了）。 |
| **2. 干活** | *(Trae Coding)* | Let Trae help you add features. <br> 让 Trae 帮你增加功能。 |
| **3. 存档** | `git commit -am "desc"` | Once done, use `-am` to add and commit tracked files directly. <br> 完成后，直接用 `-am` 合并 add 和 commit（仅限已追踪的文件）。 |
| **4. 发货** | `git push` | Sync to the cloud. <br> 同步到云端。 |

---

## 5. Troubleshooting (疑难解答)

### 5.1 Confirming Updates (确认更新是否成功)
If you pushed but don't see the files on GitHub, check the following:
如果你执行了 Push 但没在 GitHub 看到新文件，请检查以下几点：

**Check Status (检查状态):**
Run `git status`.
*   `Untracked files`: You forgot `git add .`. (忘了添加)
*   `Changes to be committed`: You forgot `git commit`. (忘了提交)
*   `nothing to commit, working tree clean`: Local is clean. (本地已处理好)

**Check Branch (检查分支):**
Run `git branch`.
*   Ensure the branch with `*` is the same one you are viewing on GitHub (usually `main`).
*   确保带 `*` 的分支和你 GitHub 网页上查看的分支一致。

### 5.2 Force Sync (强制同步三部曲)
If unsure, run these 3 commands in order to force a sync:
如果不确定哪步漏了，请直接按顺序执行这三行：

```bash
# 1. Add all changes (强制将所有改动加入暂存区)
git add .

# 2. Commit (再次提交，如果有改动的话)
git commit -m "Force update: Ensure everything is synced"

# 3. Push to main (确保推送到 main 分支)
git push origin main
```

**Understanding Output (读懂输出):**
*   `Your branch is ahead of 'origin/main' by 1 commit`: You have local changes waiting to be pushed. (本地有存档未发车)
*   `Enumerating objects... done`: Push successful. (推送成功)
*   `Everything up-to-date`: No new changes to push. (没有新改动)

### 5.3 Security Warning (安全警告)
If you see `TLS certificate verification has been disabled!`:
*   **Reason**: `git config --global http.sslVerify false` was likely used to bypass network issues.
*   **Risk**: Traffic is unencrypted and vulnerable to interception.
*   **Fix**: Ideally, enable verification: `git config --global http.sslVerify true`.
*   **原因**：可能为了解决网络问题关闭了 SSL 验证。
*   **风险**：流量未加密，存在被截获风险。
*   **建议**：在安全网络环境下，建议重新开启验证：`git config --global http.sslVerify true`。

---

## 6. CI/CD Integration (自动化集成)

### 6.1 GitHub Actions (Recommended)
We have automatically created a CI workflow for GitHub Actions at `.github/workflows/ci.yml`.
我们已在 `.github/workflows/ci.yml` 创建了 GitHub Actions 工作流。

It will run tests automatically when you push to `main` or create a Pull Request.
当您推送到 `main` 分支或创建 PR 时，它会自动运行测试。

**Key Features (主要功能):**
*   **Odoo Test**: Installs requirements and runs Odoo unit tests (if `odoo-bin` exists).
*   **Electron Test**: Installs Node.js dependencies and prepares for testing.

### 6.2 GitLab CI/CD (Legacy)
If you use GitLab, a `.gitlab-ci.yml` is also provided in the root directory.
如果您使用 GitLab，根目录下也提供了 `.gitlab-ci.yml` 文件。

---

## 7. What Next? & Recovery (下一步与恢复)

### CI/CD in Action (CI/CD 实战)
Since your files are on GitHub, you can try the following to test your pipeline:
既然文件上去了，你可以尝试以下操作来测试你的流水线：

**Use GitHub Actions (Recommended):**
Ask Trae: "Since I've pushed to GitHub, please help me create a ci.yml in .github/workflows/ migrating logic from .gitlab-ci.yml."
**如果你想用 GitHub Actions (推荐)：**
让 Trae 帮你：“既然我已经把代码传到了 GitHub，请帮我在 .github/workflows/ 下创建一个 ci.yml，把 .gitlab-ci.yml 里的测试逻辑迁移过去。”

### Recovering from AI Overwrites (手动检查代码冲突/恢复)
Now you can safely let Trae modify code. If it "overwrites" your changes unexpectedly, run:
现在你可以放心地让 Trae 修改代码了。如果它又“冲掉”了你的代码，终端输入：

```bash
# Restore a single file (恢复单个文件)
git checkout GIT_GUIDE.md

# OR / 或者

# Discard all uncommitted changes (放弃所有未提交的修改，回到最初状态)
git reset --hard HEAD
```
