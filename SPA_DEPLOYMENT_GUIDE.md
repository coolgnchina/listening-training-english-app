# Vue.js SPA 部署指南 - 解决路由404问题

## 问题描述

当前问题：
- 直接访问 `https://englishpod666.icu/login` 出现404错误
- 刷新任何前端路由页面都会404
- 通过前端导航正常，但直接URL访问失败

**根本原因：** Vue.js使用了HTML5 History模式的路由，服务器需要配置fallback到index.html

## 解决方案

### 方案1：应用完整Nginx配置（推荐）

#### 步骤1：备份当前配置
1. 登录宝塔面板
2. 进入 **网站** → 找到 `englishpod666.icu` → **设置** → **配置文件**
3. 复制当前配置并保存备份

#### 步骤2：应用新配置
1. 将项目根目录的 `nginx.conf` 文件内容复制
2. 替换宝塔面板中的网站配置
3. 点击 **保存** 并 **重载配置**

#### 步骤3：验证配置
```bash
# 在宝塔面板终端中执行
nginx -t  # 检查配置语法
nginx -s reload  # 重载配置
```

### 方案2：最小化修改（快速修复）

如果不想替换整个配置，只需在现有配置中添加：

```nginx
# 在server块中添加，确保这个location块在最后
location / {
    try_files $uri $uri/ /index.html;
}
```

**重要：** 这个配置必须放在所有其他location块之后！

### 方案3：区分前端路由和后端API

为了避免冲突，建议修改后端API使用统一前缀：

#### 修改前端API配置

```javascript
// frontend/src/config/api.js
const API_CONFIG = {
  development: {
    baseURL: 'http://127.0.0.1:5000/api'
  },
  production: {
    baseURL: 'https://www.englishpod666.icu/api'
  }
};
```

#### 对应的Nginx配置

```nginx
# 所有API请求
location /api/ {
    proxy_pass http://127.0.0.1:5000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# 前端路由fallback
location / {
    try_files $uri $uri/ /index.html;
}
```

## 部署步骤

### 1. 本地修改（可选）

如果选择方案3，修改API配置：

```bash
cd frontend
# 修改 src/config/api.js 中的生产环境配置
npm run build
```

### 2. 上传文件到服务器

```bash
# 上传构建后的文件
scp -r frontend/dist/* user@server:/www/wwwroot/englishpod666.icu/

# 或使用宝塔面板文件管理器上传
```

### 3. 配置Nginx

按照上述方案1或方案2配置Nginx

### 4. 启动后端服务

确保Python后端服务正在运行：

```bash
cd /www/wwwroot/englishpod666.icu/backend
python app.py
```

或在宝塔面板的Python项目管理器中启动

### 5. 验证修复

1. **测试前端路由：**
   - 直接访问 `https://englishpod666.icu/login`
   - 刷新页面确认不再404
   - 测试其他路由如 `/register`, `/courses` 等

2. **测试后端API：**
   - 验证码显示正常
   - 登录注册功能正常
   - 检查浏览器开发者工具网络请求

## 常见问题排查

### 问题1：配置后仍然404

**检查项：**
- Nginx配置语法是否正确：`nginx -t`
- 是否重载了配置：`nginx -s reload`
- `try_files` 配置是否在最后一个location块

### 问题2：API请求失败

**检查项：**
- 后端服务是否运行：`ps aux | grep python`
- 端口是否监听：`netstat -tlnp | grep :5000`
- 防火墙是否开放端口

### 问题3：静态资源加载失败

**检查项：**
- 文件权限：`chmod -R 755 /www/wwwroot/englishpod666.icu`
- 文件所有者：`chown -R www:www /www/wwwroot/englishpod666.icu`

## 监控和维护

### 日志查看

```bash
# 查看访问日志
tail -f /www/wwwlogs/englishpod666.icu.log

# 查看错误日志
tail -f /www/wwwlogs/englishpod666.icu.error.log

# 查看Nginx错误日志
tail -f /www/wwwlogs/nginx_error.log
```

### 性能优化

1. **启用Gzip压缩**（已在配置中包含）
2. **设置静态资源缓存**（已在配置中包含）
3. **使用CDN**（可选）

### 安全建议

1. **定期更新SSL证书**
2. **监控服务器资源使用**
3. **定期备份数据库和配置文件**
4. **设置防火墙规则**

## Git部署流程

### 自动化部署脚本

创建 `deploy.sh` 脚本：

```bash
#!/bin/bash
# 部署脚本

echo "开始部署..."

# 拉取最新代码
git pull origin main

# 构建前端
cd frontend
npm install
npm run build

# 复制文件到网站目录
cp -r dist/* /www/wwwroot/englishpod666.icu/

# 重启后端服务（如果使用PM2）
# pm2 restart listening-training

echo "部署完成！"
```

### 使用方法

```bash
# 在服务器上执行
chmod +x deploy.sh
./deploy.sh
```

## 总结

核心解决方案是在Nginx配置中添加：

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

这个配置告诉Nginx：
1. 首先尝试找到请求的文件
2. 如果找不到，尝试作为目录
3. 最后fallback到index.html（让Vue路由处理）

按照本指南操作后，SPA路由404问题应该得到完全解决。