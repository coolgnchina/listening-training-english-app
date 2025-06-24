# 听力训练应用

这是一个交互式的听力训练网站，旨在帮助用户通过完成句子来提高英语听力技能。

## 技术框架

本应用采用前后端分离的架构。

### 前端

- **Vue 3**: 用于构建用户界面的现代化 JavaScript 框架。
- **Vite**: 提供快速开发体验的构建工具。
- **TypeScript**: 为 JavaScript 添加了类型系统，增强了代码的健壮性。
- **Vue Router**: 用于处理页面导航。

### 后端

- **Flask**: 一个轻量级的 Python Web 框架。
- **SQLite**: 一个简单的文件型数据库，用于存储课程信息。

## 目录和文件说明

```
.
├── backend/            # 后端代码目录
│   ├── app.py          # Flask 应用主文件，包含所有 API 接口
│   ├── app.db          # SQLite 数据库文件
│   ├── requirements.txt# Python 依赖包列表
│   └── uploads/        # 存放上传的音频和字幕文件
│
├── frontend/           # 前端代码目录
│   ├── src/
│   │   ├── components/   # Vue 组件，如课程列表、课程详情等
│   │   ├── views/        # 页面级组件
│   │   ├── router/       # 路由配置
│   │   └── main.ts       # 前端应用入口文件
│   ├── index.html      # 网站主 HTML 文件
│   ├── package.json    # Node.js 依赖和项目脚本配置
│   └── vite.config.ts  # Vite 配置文件
└── README.md           # 你正在阅读的这个文件
```

## 环境要求

在开始之前，请确保您的电脑上安装了以下软件：

- **Node.js**: (版本 >= 16.x) 用于运行前端应用。
- **Python**: (版本 >= 3.8) 用于运行后端服务。

## 部署指南

要运行这个项目，您需要分别启动后端服务和前端应用。

### 1. 启动后端服务

后端服务负责处理数据和逻辑。建议使用虚拟环境以隔离项目依赖。

- **进入后端目录**:
  ```bash
  cd backend
  ```
- **创建并激活虚拟环境** (可选，但推荐):
  ```bash
  # Windows
  python -m venv .venv
  .venv\Scripts\activate

  # macOS / Linux
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- **安装依赖**: 
  ```bash
  pip install -r requirements.txt
  ```
- **启动服务**: 
  ```bash
  flask run
  ```

当您在终端看到类似 `Running on http://127.0.0.1:5000` 的信息时，表示后端服务已成功启动。

### 2. 启动前端应用

前端应用是用户直接与之交互的界面。

- **进入前端目录** (请打开一个新的终端窗口):
  ```bash
  cd frontend
  ```
- **安装依赖** (如果第一次运行或者依赖有更新):
  ```bash
  npm install
  ```
- **启动应用**:
  ```bash
  npm run dev
  ```

启动后，您会在终端看到一个本地访问地址，通常是 `http://localhost:5173`。在浏览器中打开这个地址，您就可以开始使用这个听力训练应用了。

**注意**: 请确保后端和前端服务都在运行中，这样网站才能正常工作。

## PaaS 平台部署 (推荐)

对于希望简化部署流程的开发者，我们推荐使用平台即服务 (PaaS) 平台，如 [Render](https://render.com/) 或 [Heroku](https://www.heroku.com/)。这些平台可以自动处理服务器配置、扩展和维护，让您专注于代码。

以下是在 Render 上部署此项目的分步指南：

### 1. 准备工作

- **注册 Render 账号**: 访问 [Render](https://render.com/) 并创建一个免费账号。
- **连接 GitHub**: 将您的项目代码推送到一个 GitHub 仓库，并在 Render 中授权访问该仓库。

### 2. 部署后端服务 (Flask)

1.  在 Render Dashboard 中，点击 “New +” -> “Web Service”。
2.  选择您的项目仓库并连接。
3.  填写以下配置：
    -   **Name**: `my-listening-app-backend` (或您喜欢的任何名称)
    -   **Root Directory**: `backend`
    -   **Environment**: `Python 3`
    -   **Region**: 选择离您最近的区域。
    -   **Branch**: `main` (或您的主分支)
    -   **Build Command**: `pip install -r requirements.txt && flask init-db` (我们需要一个命令来初始化数据库，稍后会创建它)
    -   **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`

4.  点击 “Create Web Service”。Render 将自动拉取代码、安装依赖并启动您的后端服务。

#### 创建数据库初始化命令

为了让 `flask init-db` 命令生效，我们需要在 `backend/app.py` 中添加一个自定义的 Flask CLI 命令。请在 `app.py` 文件末尾添加以下代码：

```python
import click
from flask.cli import with_appcontext

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.create_all()
    click.echo('Initialized the database.')

app.cli.add_command(init_db_command)
```

### 3. 部署前端服务 (Vite)

1.  在 Render Dashboard 中，点击 “New +” -> “Static Site”。
2.  选择同一个项目仓库并连接。
3.  填写以下配置：
    -   **Name**: `my-listening-app-frontend` (或您喜欢的任何名称)
    -   **Root Directory**: `frontend`
    -   **Branch**: `main` (或您的主分支)
    -   **Build Command**: `npm install && npm run build`
    -   **Publish Directory**: `dist`

4.  在 “Environment Variables” 部分，添加一个环境变量，将前端连接到您的后端 API：
    -   **Key**: `VITE_API_BASE_URL`
    -   **Value**: 复制您刚刚创建的后端服务的 URL (例如 `https://my-listening-app-backend.onrender.com`)。

5.  点击 “Create Static Site”。Render 将构建您的 Vue 应用并将其部署到全球 CDN。

### 4. 完成

部署完成后，您可以通过 Render 提供的 URL 访问您的前端应用。它将自动与部署在 Render 上的后端服务进行通信。

---

## 生产环境部署

### 服务器环境推荐

本部署指南主要针对 **Linux** 或 **macOS** 等 Unix-like 操作系统，因为推荐使用的 Gunicorn 在这些环境下表现最佳且最常用。

虽然也可以在 Windows 服务器上部署，但通常需要使用不同的工具（例如 Waitress 或 IIS + HttpPlatformHandler），配置步骤会有所不同。

### 部署步骤

当您想将网站部署到真实的服务器上时，步骤会略有不同。您需要将前端应用“构建”成静态文件，然后由后端服务来统一提供访问。

### 1. 构建前端应用

- **进入前端目录**:
  ```bash
  cd frontend
  ```
- **执行构建命令**:
  ```bash
  npm run build
  ```
  这个命令会生成一个 `dist` 文件夹，里面包含了所有优化和压缩过的前端静态文件（HTML, CSS, JavaScript）。

### 2. 准备后端

- 将前端构建好的 `dist` 文件夹整个复制到 `backend` 目录下。
- 后端需要配置为可以托管这些静态文件。这通常需要在 `app.py` 中进行一些修改，以确保当用户访问网站时，Flask能够返回 `dist/index.html` 文件。

### 3. 在服务器上运行

在生产环境中，不推荐使用 `flask run` 来启动服务。您应该使用一个更稳定、性能更好的 WSGI 服务器，例如 Gunicorn。

- **安装 Gunicorn**:
  ```bash
  pip install gunicorn
  ```
- **使用 Gunicorn 启动应用** (在 `backend` 目录下运行):
  ```bash
  gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
  ```
  这会启动后端服务，并监听在 `8000` 端口。现在，通过服务器的 IP 地址和端口（例如 `http://YOUR_SERVER_IP:8000`）就可以访问您的听力训练网站了。

**提示**: 为了获得更好的性能和安全性，通常还会在前面再加一个像 Nginx 这样的反向代理服务器，但这属于更高级的部署策略。