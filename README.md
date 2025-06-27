# 英语听力训练系统

这是一个交互式的英语听力训练网站，旨在帮助用户通过完成句子来提高英语听力技能。系统采用现代化的前后端分离架构，提供完整的用户管理、课程管理和听力练习功能。

## ✨ 主要功能

### 🎯 核心功能
- **听力练习**: 基于音频和字幕文件的交互式听力训练
- **用户系统**: 完整的用户注册、登录、邮箱验证功能
- **课程管理**: 支持课程的创建、编辑、删除和管理
- **进度跟踪**: 用户学习进度和成绩记录
- **积分系统**: 爱心积分机制，增强学习动力

### 👥 用户角色
- **普通用户**: 进行听力练习，查看个人进度
- **管理员**: 管理课程内容，用户管理，系统维护

## 🛠 技术架构

### 前端技术栈
- **Vue 3**: 现代化的渐进式JavaScript框架
- **TypeScript**: 类型安全的JavaScript超集
- **Vite**: 快速的前端构建工具
- **Vue Router**: 单页应用路由管理
- **Pinia**: 状态管理库
- **Element Plus**: UI组件库
- **Axios**: HTTP客户端

### 后端技术栈
- **Flask**: 轻量级Python Web框架
- **SQLAlchemy**: Python SQL工具包和ORM
- **SQLite**: 轻量级数据库
- **JWT**: JSON Web Token身份验证
- **Flask-CORS**: 跨域资源共享支持
- **SRT**: 字幕文件解析
- **Pillow**: 图像处理（验证码生成）

## 📁 项目结构

```
听力训练001/
├── backend/                    # 后端服务
│   ├── app.py                 # Flask应用主文件
│   ├── requirements.txt       # Python依赖包
│   ├── uploads/              # 文件上传目录
│   │   ├── audio/           # 音频文件存储
│   │   └── subtitles/       # 字幕文件存储
│   └── instance/             # 数据库文件目录
│       └── database.db      # SQLite数据库
├── frontend/                  # 前端应用
│   ├── src/                  # 源代码目录
│   │   ├── components/      # Vue组件
│   │   │   ├── CourseDetail.vue    # 课程详情组件
│   │   │   ├── Login.vue           # 登录组件
│   │   │   ├── Register.vue        # 注册组件
│   │   │   ├── CourseManagement.vue # 课程管理组件
│   │   │   ├── UserManagement.vue   # 用户管理组件
│   │   │   └── ...
│   │   ├── views/           # 页面视图
│   │   │   ├── HomeView.vue        # 首页
│   │   │   ├── AboutView.vue       # 关于页面
│   │   │   ├── AdminView.vue       # 管理员页面
│   │   │   └── ...
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # 状态管理
│   │   ├── assets/          # 静态资源
│   │   └── App.vue          # 根组件
│   ├── package.json         # 前端依赖配置
│   ├── vite.config.ts       # Vite构建配置
│   ├── tsconfig.json        # TypeScript配置
│   └── index.html           # 入口HTML文件
├── start.bat                  # Windows启动脚本
└── README.md                  # 项目文档
```

## 🔧 环境要求

在开始之前，请确保您的系统已安装以下软件：

### 必需软件
- **Node.js** (版本 16.0+ 推荐): 用于前端开发和构建
- **Python** (版本 3.8+ 推荐): 用于后端服务
- **npm** 或 **yarn**: Node.js包管理器
- **pip**: Python包管理器

### 推荐工具
- **Git**: 版本控制
- **VS Code**: 代码编辑器
- **Postman**: API测试工具

## 🚀 快速开始

### 方法一：使用启动脚本（推荐）

**Windows用户**:
```bash
# 双击运行或在命令行执行
start.bat
```

这个脚本会自动：
1. 启动后端Flask服务（端口5000）
2. 启动前端开发服务器（端口5173）
3. 自动打开浏览器访问应用

### 方法二：手动启动

#### 1. 启动后端服务

```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install -r requirements.txt

# 启动Flask应用
python app.py
```

后端服务将在 `http://localhost:5000` 运行

#### 2. 启动前端应用

```bash
# 新开终端，进入前端目录
cd frontend

# 安装Node.js依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:5173` 运行

#### 3. 访问应用

打开浏览器访问 `http://localhost:5173` 开始使用！

### 默认管理员账号

- **用户名**: admin@example.com
- **密码**: admin123

> ⚠️ **注意**: 首次运行时请修改默认管理员密码

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

## 💻 开发指南

### 开发环境设置

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd 听力训练001
   ```

2. **后端开发环境**
   ```bash
   cd backend
   
   # 创建虚拟环境（推荐）
   python -m venv venv
   
   # 激活虚拟环境
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   ```

3. **前端开发环境**
   ```bash
   cd frontend
   npm install
   ```

### 开发命令

#### 后端开发
```bash
# 启动开发服务器
python app.py

# 数据库操作
flask shell  # 进入Flask shell
```

#### 前端开发
```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint

# 代码格式化
npm run format

# 运行测试
npm run test
```

### API接口文档

#### 用户相关
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/verify-email` - 邮箱验证
- `GET /api/user/profile` - 获取用户信息

#### 课程相关
- `GET /api/courses` - 获取课程列表
- `POST /api/courses` - 创建课程（管理员）
- `GET /api/courses/<id>` - 获取课程详情
- `PUT /api/courses/<id>` - 更新课程（管理员）
- `DELETE /api/courses/<id>` - 删除课程（管理员）

#### 练习相关
- `POST /api/practice/submit` - 提交练习答案
- `GET /api/practice/progress` - 获取学习进度

## 📖 使用说明

### 普通用户

1. **注册账号**: 使用邮箱注册并验证
2. **选择课程**: 浏览可用的听力训练课程
3. **开始练习**: 听音频，完成句子填空
4. **查看进度**: 在个人中心查看学习进度和成绩

### 管理员

1. **课程管理**: 创建、编辑、删除课程
2. **文件上传**: 上传音频和字幕文件
3. **用户管理**: 查看和管理用户信息
4. **数据统计**: 查看系统使用统计

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

## 🔧 宝塔面板部署

### 环境要求
- Linux服务器（CentOS 7+/Ubuntu 18+）
- 宝塔面板 7.0+
- Python 3.8+
- Node.js 16+
- Nginx

### 部署步骤

1. **安装宝塔面板**
   ```bash
   # CentOS
   yum install -y wget && wget -O install.sh http://download.bt.cn/install/install_6.0.sh && sh install.sh
   
   # Ubuntu
   wget -O install.sh http://download.bt.cn/install/install-ubuntu_6.0.sh && sudo bash install.sh
   ```

2. **安装运行环境**
   - 在宝塔面板中安装：Nginx、Python项目管理器、Node.js版本管理器、PM2管理器

3. **上传项目文件**
   - 方法一：通过宝塔文件管理器上传压缩包并解压
   - 方法二：使用Git克隆（如果服务器可以访问GitHub）
   - 方法三：使用SCP/SFTP工具上传

4. **配置后端**
   ```bash
   cd /www/wwwroot/listening-app/backend
   pip install -r requirements.txt
   ```

5. **配置前端**
   ```bash
   cd /www/wwwroot/listening-app/frontend
   npm install
   npm run build
   ```

6. **配置Nginx站点**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       # 前端静态文件
       location / {
           root /www/wwwroot/listening-app/frontend/dist;
           try_files $uri $uri/ /index.html;
       }
       
       # 后端API
       location /api {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
       
       # 文件上传目录
       location /uploads {
           alias /www/wwwroot/listening-app/backend/uploads;
           expires 30d;
       }
       
       # 文件上传大小限制
       client_max_body_size 100M;
   }
   ```

7. **启动服务**
   - 在Python项目管理器中添加项目
   - 设置项目路径：`/www/wwwroot/listening-app/backend`
   - 设置启动文件：`app.py`
   - 启动项目

### 注意事项

- 确保文件权限正确：`chmod -R 755 /www/wwwroot/listening-app/`
- 上传目录需要写权限：`chmod -R 777 /www/wwwroot/listening-app/backend/uploads/`
- 配置SSL证书以启用HTTPS
- 设置防火墙规则，开放必要端口
- 定期备份数据库和上传文件

## ❓ 常见问题

### 安装问题

**Q: npm install 失败怎么办？**
A: 尝试以下解决方案：
```bash
# 清除缓存
npm cache clean --force

# 使用国内镜像
npm config set registry https://registry.npmmirror.com

# 重新安装
rm -rf node_modules package-lock.json
npm install
```

**Q: Python依赖安装失败？**
A: 尝试以下解决方案：
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 如果是权限问题
pip install -r requirements.txt --user
```

### 运行问题

**Q: 前端无法连接后端？**
A: 检查以下几点：
- 后端服务是否正常启动
- 前端API地址配置是否正确
- 防火墙是否阻止了端口访问
- CORS配置是否正确

**Q: 文件上传失败？**
A: 检查以下几点：
- 上传目录是否存在且有写权限
- 文件大小是否超过限制
- 文件格式是否支持
- 服务器磁盘空间是否充足

**Q: 数据库连接失败？**
A: 检查以下几点：
- 数据库文件路径是否正确
- 目录权限是否正确
- SQLite是否正确安装

### 性能优化

**Q: 如何提高应用性能？**
A: 可以考虑以下优化：
- 使用Nginx作为反向代理
- 启用Gzip压缩
- 配置静态文件缓存
- 使用CDN加速
- 数据库查询优化

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. **Fork项目**
2. **创建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **创建Pull Request**

### 开发规范

- 遵循现有的代码风格
- 添加适当的注释
- 编写测试用例
- 更新相关文档

### 报告问题

如果您发现了bug或有功能建议，请：
1. 检查是否已有相关issue
2. 创建新的issue并详细描述问题
3. 提供复现步骤和环境信息

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

- Vue.js 团队提供的优秀前端框架
- Flask 团队提供的轻量级后端框架
- 所有开源库的维护者们

## 📞 联系我们

如果您有任何问题或建议，请通过以下方式联系我们：

- 创建 GitHub Issue
- 发送邮件至：[your-email@example.com]
- 加入我们的讨论群：[群号或链接]

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！