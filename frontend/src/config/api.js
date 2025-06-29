// API配置
const API_CONFIG = {
  // 开发环境
  development: {
    baseURL: 'http://127.0.0.1:5000'
  },
  // 生产环境 - 修复域名
  production: {
    baseURL: 'https://englishpod666.icu'  // 移除 www 前缀
  }
};

// 获取当前环境
const getEnvironment = () => {
  // 在Vite中，import.meta.env.MODE 表示当前模式
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return import.meta.env.MODE === 'production' ? 'production' : 'development';
  }
  // 备用检测方法
  return window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'development' 
    : 'production';
};

// 获取API基础URL
export const getApiBaseUrl = () => {
  const env = getEnvironment();
  return API_CONFIG[env].baseURL;
};

// 构建完整的API URL
export const buildApiUrl = (endpoint) => {
  const env = getEnvironment();
  const baseUrl = API_CONFIG[env].baseURL;
  // 确保endpoint以/开头
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  if (env === 'production') {
    // 生产环境下，我们依赖Nginx代理，所以直接使用相对路径
    return `/api${cleanEndpoint}`;
  }
  
  // 开发环境下，使用完整的URL，由Vite开发服务器代理
  return `${baseUrl}${cleanEndpoint}`;
};

// 导出配置对象
export default API_CONFIG;