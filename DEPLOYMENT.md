# 部署说明 - 验证码加载问题解决方案

## 问题描述
验证码在服务器上显示"加载中..."，无法正常显示。

## 问题原因
1. 前端代码中硬编码了本地API地址 `http://127.0.0.1:5000`
2. 服务器上后端API服务未正确配置或未运行
3. 前后端API地址不匹配

## 解决方案

### 1. 前端修改（已完成）
- 创建了 `frontend/src/config/api.js` 配置文件
- 修改了 `Register.vue` 和 `auth.js` 使用动态API地址
- 生产环境API地址设置为：`https://www.englishpod666.icu`

### 2. 重新构建前端
```bash
cd frontend
npm run build
```

### 3. 上传新的前端文件到服务器
将 `frontend/dist/` 目录下的所有文件上传到服务器的网站目录：
```
/www/wwwroot/listening-training-english-app/frontend/dist/
```

### 4. 服务器后端配置

#### 方案A：使用宝塔面板配置Python项目
1. 在宝塔面板中创建Python项目
2. 上传后端代码到服务器
3. 安装依赖：`pip install -r requirements.txt`
4. 配置项目运行

#### 方案B：使用Nginx反向代理
在Nginx配置中添加API代理：
```nginx
server {
    listen 443 ssl;
    server_name www.englishpod666.icu;
    
    # 静态文件
    location / {
        root /www/wwwroot/listening-training-english-app/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理到后端
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 验证码等非API路由
    location ~ ^/(captcha|login|register|verify-email|resend-verification)$ {
        proxy_pass http://127.0.0.1:5000$request_uri;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 上传文件访问
    location /uploads/ {
        proxy_pass http://127.0.0.1:5000/uploads/;
    }
}
```

#### 方案C：修改后端路由统一使用/api前缀
在 `backend/app.py` 中修改验证码路由：
```python
@app.route('/api/captcha', methods=['GET'])
def get_captcha():
    # 现有代码
```

### 5. 启动后端服务
```bash
cd backend
python app.py
```

### 6. 验证修复
1. 访问 `https://www.englishpod666.icu`
2. 进入注册页面
3. 检查验证码是否正常显示
4. 检查浏览器开发者工具的网络请求

## 推荐部署步骤

1. **立即执行**：重新构建前端并上传
2. **配置后端**：使用宝塔面板或Nginx代理
3. **测试验证**：确认验证码正常显示
4. **监控日志**：检查错误日志确保稳定运行

## 注意事项

- 确保服务器防火墙开放5000端口（如果直接运行后端）
- 检查SSL证书是否包含API域名
- 生产环境建议使用进程管理工具（如PM2、Supervisor）管理后端服务
- 定期检查后端服务状态