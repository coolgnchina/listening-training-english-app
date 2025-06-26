<template>
  <div class="auth-container">
    <div class="auth-form card">
      <h2 class="page-title">注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username" class="form-label">用户名</label>
          <input type="text" id="username" v-model="username" required placeholder="请输入您的用户名" class="form-input">
        </div>

        <div class="form-group">
          <label for="password" class="form-label">密码</label>
          <input type="password" id="password" v-model="password" required placeholder="请输入您的密码（至少6位）" class="form-input">
          <div v-if="password && password.length < 6" class="password-hint">密码长度至少为6位</div>
        </div>
        <div class="form-group">
          <label for="captcha" class="form-label">验证码</label>
          <div class="captcha-container">
            <input type="text" id="captcha" v-model="captcha" required placeholder="请输入验证码" class="form-input captcha-input">
            <div class="captcha-image" @click="refreshCaptcha">
              <img v-if="captchaImage" :src="captchaImage" alt="验证码" />
              <div v-else class="captcha-loading">加载中...</div>
            </div>
          </div>
          <button type="button" class="btn-refresh" @click="refreshCaptcha">刷新验证码</button>
        </div>
        <button type="submit" class="btn btn-primary submit-btn">注册</button>
        <p v-if="message" :class="messageType" class="message">{{ message }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const username = ref('');

const password = ref('');
const captcha = ref('');
const captchaImage = ref('');
const captchaId = ref('');
const message = ref('');
const messageType = ref('');
const authStore = useAuthStore();
const router = useRouter();

// 获取验证码
const getCaptcha = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/captcha');
    if (response.ok) {
      const data = await response.json();
      captchaImage.value = data.image;
      captchaId.value = data.id;
    }
  } catch (error) {
    console.error('获取验证码失败:', error);
  }
};

// 刷新验证码
const refreshCaptcha = () => {
  getCaptcha();
};

// 页面加载时获取验证码
getCaptcha();

const handleRegister = async () => {
  // 基本验证
  if (!username.value || !password.value) {
    message.value = '请填写所有必填字段';
    messageType.value = 'error';
    return;
  }
  
  if (password.value.length < 6) {
    message.value = '密码长度至少为6位';
    messageType.value = 'error';
    return;
  }
  
  if (!captcha.value) {
    message.value = '请输入验证码';
    messageType.value = 'error';
    return;
  }
  
  const result = await authStore.register(username.value, password.value, captcha.value, captchaId.value);
  if (result.success) {
    message.value = '注册成功！';
    messageType.value = 'success';
    // 清空表单
    username.value = '';

    password.value = '';
    captcha.value = '';
    // 3秒后跳转到登录页面
    setTimeout(() => router.push('/login'), 3000);
  } else {
    message.value = result.message || '注册失败，请检查输入信息。';
    messageType.value = 'error';
    // 注册失败后刷新验证码
    refreshCaptcha();
    captcha.value = '';
  }
};
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: var(--spacing-lg);
  background: var(--gradient-primary);
}

.auth-form {
  width: 100%;
  max-width: 450px;
  padding: var(--spacing-2xl);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.submit-btn {
  width: 100%;
  padding: var(--spacing-md);
  font-size: var(--font-size-lg);
  margin-top: var(--spacing-md);
}

.message {
  text-align: center;
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-md);
  border: 1px solid;
}

.message.success {
  color: var(--success-color);
  background: rgba(40, 167, 69, 0.1);
  border-color: rgba(40, 167, 69, 0.2);
}

.message.error {
  color: var(--danger-color);
  background: rgba(220, 53, 69, 0.1);
  border-color: rgba(220, 53, 69, 0.2);
}

/* 验证码样式 */
.captcha-container {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.captcha-input {
  flex: 1;
}

.captcha-image {
  width: 120px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: #f5f5f5;
  transition: all var(--transition-normal);
}

.captcha-image:hover {
  border-color: var(--primary-color);
  background: #f0f0f0;
}

.captcha-image img {
  max-width: 100%;
  max-height: 100%;
  border-radius: var(--border-radius-sm);
}

.captcha-loading {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.btn-refresh {
  background: none;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
  margin-top: var(--spacing-xs);
}

.btn-refresh:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.password-hint {
  color: #e74c3c;
  font-size: 12px;
  margin-top: 5px;
}

@media (max-width: 768px) {
  .auth-container {
    padding: var(--spacing-md);
  }
  
  .auth-form {
    padding: var(--spacing-xl);
  }
  
  .captcha-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .captcha-image {
    width: 100%;
    height: 50px;
  }
}
</style>